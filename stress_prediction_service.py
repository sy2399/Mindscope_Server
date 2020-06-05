import pickle

from feature_extraction import Features
from Mindscope_Server import models
import threading
import schedule
import time
import grpc
import pandas as pd
import json
import datetime

import et_service_pb2
import et_service_pb2_grpc

from stress_model import StressModel

# Notes:
#################################################################################################
# This is the Mindscope Server application
# It runs a prediction_task() function at every prediction time (prediction_times)
# Inside prediction task we have following steps for each user in the study:
# Step0. check users day num if it's more than 14 days, only then extract features for 14 days and init the model
# Step1: retrieve the users' data from the gRPC server (John) - Done
# Step2: extract features from retrieved data (John) - Done
# Step3: pre-process and normalize the extracted features (Soyoung) - Need to integrate
# Step4: init StressModel by taking pre-processed data from DB and normalizing (Soyoung) - Need to integrate
# Step5: make prediction using current features with that model (Soyoung) - Need to integrate
# Step6: save current features prediction as label to DB (John)
# Step7: return prediction to gRPC server (John)
# Step8: check user self report and update the DB of pre-processed features with reported stress label if there is self report from user
#################################################################################################


prediction_times = [10, 14, 18, 22]
run_service = None
thread = None
grpc_stub = None
grpc_channel = None

survey_duration = 14  # in days


def start():
    global run_service, thread
    run_service = True
    thread = threading.Thread(target=service_routine())
    thread.start()


def stop():
    global run_service
    run_service = False


def service_routine():
    job10 = schedule.every().day.at("10:00").do(prediction_task, 0)
    job14 = schedule.every().day.at("14:00").do(prediction_task, 1)
    job18 = schedule.every().day.at("18:00").do(prediction_task, 2)
    job22 = schedule.every().day.at("22:00").do(prediction_task, 3)

    while run_service:
        schedule.run_pending()
        time.sleep(1)

    schedule.cancel_job(job=job10)
    schedule.cancel_job(job=job14)
    schedule.cancel_job(job=job18)
    schedule.cancel_job(job=job22)


def prediction_task(i):
    print("Prediction task for {} is running... ".format(prediction_times[i]))
    grpc_init()

    now_datetime = datetime.datetime.now()
    end_time = int(now_datetime.replace(hour=prediction_times[i], minute=0, second=0).timestamp()) * 1000
    if i == 0:
        start_time = end_time - (4 * 3600 * 1000)  # hard coded 4 hours (difference between prediction times during the day)
    else:
        start_time = int(now_datetime.replace(hour=prediction_times[i - 1], minute=0, second=0).timestamp()) * 1000

    users_info = grpc_load_user_emails()
    ema_order = i + 1
    for user_email, id_day in users_info.items():
        user_id = id_day['uid']  # user[1]=user_id
        day_num = id_day['dayNum']  # user[1]=user_id
        sm = StressModel(uid=user_email, dayNo=day_num, emaNo=ema_order)

        # TODO: 0. check users day num if it's more than 14 days, only then extract features for 14 days and init the model
        if day_num > survey_duration:
            # if the first day and the first ema order after 14days
            if day_num == 15 and ema_order == 1:
                # first model init based on 14 days data

                start_time = 0  # from the very beginning of data collection
                end_time = int(now_datetime.replace(hour=prediction_times[i], minute=0, second=0).timestamp()) * 1000

                data = grpc_load_user_data(start_ts=start_time, end_ts=end_time, uid=user_email)
                features = Features(uid=user_email, dataset=data)
                df = pd.DataFrame(features.extract())
                df_features = df[df['User id'] == user_email]

                # preprocessing and saving the result
                df_preprocessed = sm.preprocessing(df_features)
                with open('data_result/' + str(user_email) + "_features.p", 'wb') as file:
                    pickle.dump(df_preprocessed, file)

                # normalizing
                norm_df = sm.normalizing("default", df_preprocessed, None)

                # init model
                sm.initModel(norm_df)
            else:
                # TODO: 1. retrieve the data from the gRPC server (Done)
                # get all user data from gRPC server between start_ts and end_ts
                data = grpc_load_user_data(start_ts=start_time, end_ts=end_time, uid=user_email)

                # TODO: 2. extract features from retrieved data (Done)
                with open('data_result/' + str(user_email) + "_features.p", 'rb') as file:
                    step1_preprocessed = pickle.load(file)
                features = Features(uid=user_email, dataset=data)
                df = pd.DataFrame(features.extract())
                df_features = df[df['User id'] == user_email]
                new_row = df_features.iloc[10, :]
                new_row_df = pd.DataFrame(new_row).transpose()
                # TODO: 3. pre-process and normalize the extracted features (Soyoung)
                new_row_preprocessed = sm.preprocessing(new_row_df)
                norm_df = sm.normalizing("new", step1_preprocessed, new_row_preprocessed)
                # TODO: 4. init StressModel here (Soyoung)
                # get test dasta
                new_row_for_test = norm_df[(norm_df['Day'] == day_num) & (norm_df['EMA order'] == ema_order)]

                ## get trained model
                with open('model_result/' + str(user_email) + "_model.p", 'rb') as file:
                    initModel = pickle.load(file)

                # TODO: 5. make prediction using current features with that model (Soyoung)

                features = StressModel.feature_df_with_state['features'].values

                y_pred = initModel.predict(new_row_for_test[features])

                new_row['Sterss_label'] = y_pred

                # TODO: 6. save current features prediction as label to DB (Soyoung)
                # insert a new pre-processed feature entry in DB with predicted label

                # DATA- , Model UPDATE
                update_df = pd.concat([step1_preprocessed.reset_index(drop=True), new_row_preprocessed.reset_index(drop=True)])

                with open('data_result/' + str(user_email) + "_features.p", 'wb') as file:
                    pickle.dump(update_df, file)

                # TODO: 7. save prediction in DB and return it to gRPC server (John)
                # Send the prediction with "STRESS_PREDICTION" data source and "day_num ema_order prediction_value" value
                user_all_labels = list(set(step1_preprocessed['Stress_label']))
                model_results = list(sm.getSHAP(user_all_labels, y_pred, new_row_for_test, initModel))  # saves results on ModelResult table in DB
                # TODO: construct a message from model results and return it to gRPC server

                # TODO: 8. check user self report and update the DB of pre-processed features with reported stress label if if there is self report from user
                # check 'SELF_STRESS_REPORT' data source for user and run retrain if needed and retrain
                # region Retrain the models with prev self reports
                sr_day_num = 0
                sr_ema_order = 0
                sr_value = -1  # self report value
                if data['SELF_STRESS_REPORT'][-1][1]:  # data['SELF_STRESS_REPORT'][-1][1] takes the value of the latest SELF_STRESS_REPORT data source
                    sr_day_num, sr_ema_order, sr_value = [int(i) for i in data['SELF_STRESS_REPORT'][-1][1].split(" ")]

                model_result_to_update = models.ModelResult.objects.get(uid=user_email, day_num=sr_day_num, ema_order=sr_ema_order, prediction_result=sr_value)
                # check if this result was not already updated by the user, if it wasn't then update the user tag and re-train the model
                if model_result_to_update.user_tag == False:
                    sm.update(sr_value)
    grpc_close()


def grpc_init():
    global grpc_stub, grpc_channel
    # open a gRPC channel
    channel = grpc.insecure_channel('165.246.21.202:50051')

    # create a stub (client)
    grpc_stub = et_service_pb2_grpc.ETServiceStub(channel)


def grpc_close():
    global grpc_channel
    grpc_channel.close()


def grpc_load_user_emails():
    global grpc_stub

    user_info = {}
    # retrieve participant emails
    request = et_service_pb2.RetrieveParticipantsRequestMessage(
        userId=2,
        email='nnarziev@nsl.inha.ac.kr',
        campaignId=10
    )
    response = grpc_stub.retrieveParticipants(request)
    if not response.doneSuccessfully:
        return False
    for idx, email in enumerate(response.email):
        user_info[email] = {}
        user_info[email]['uid'] = response.userId[idx]
        # user_info.append((email, response.userId[idx]))

    for email, id in user_info.items():
        request = et_service_pb2.RetrieveParticipantStatisticsRequestMessage(
            userId=2,
            email='nnarziev@nsl.inha.ac.kr',
            targetEmail=email,
            targetCampaignId=10
        )
        response = grpc_stub.retrieveParticipantStatistics(request)
        if not response.doneSuccessfully:
            return False
        user_info[email]['dayNum'] = joinTimestampToDayNum(response.campaignJoinTimestamp)

    return user_info


def grpc_load_user_data(start_ts, end_ts, uid):
    global grpc_stub
    # retrieve campaign details --> data source ids
    request = et_service_pb2.RetrieveCampaignRequestMessage(
        userId=2,
        email='nnarziev@nsl.inha.ac.kr',
        campaignId=10
    )
    response = grpc_stub.retrieveCampaign(request)
    if not response.doneSuccessfully:
        return False
    data_sources = {}
    for data_source in json.loads(response.configJson):
        data_sources[data_source['name']] = data_source['data_source_id']

    # retrieve data of each participant
    data = {}
    for data_source_name in data_sources:
        data[data_source_name] = []
        request = et_service_pb2.RetrieveFilteredDataRecordsRequestMessage(
            userId=2,
            email='nnarziev@nsl.inha.ac.kr',
            targetEmail=uid,
            targetCampaignId=10,
            targetDataSourceId=data_sources[data_source_name],
            fromTimestamp=start_ts,
            tillTimestamp=end_ts
        )
        response = grpc_stub.retrieveFilteredDataRecords(request)
        if response.doneSuccessfully:
            for ts, vl in zip(response.timestamp, response.value):
                data[data_source_name] += [(ts, vl)]
    # print(data)
    return data


def grpc_send_user_data(timestamp, value):
    global grpc_stub
    pass


def joinTimestampToDayNum(joinTimestamp):
    # TODO: write a code to compute the current day number for participant
    nowTime = int(datetime.datetime.now().timestamp()) * 1000
    return (nowTime - joinTimestamp) / 1000 / 3600 / 24
