import pandas as pd
import datetime
from urllib.request import urlopen
from urllib.request import HTTPError
from bs4 import BeautifulSoup


def number_in_range(number, start, end):
    if start <= number <= end:
        return True
    else:
        return False


def get_filename_from_data_src(filenames, data_src, username):
    for filename in filenames:
        if username in filename and data_src in filename:
            return filename


class Features:
    EMA_RESPONSE_EXPIRE_TIME = 3600  # in seconds
    LOCATION_HOME = "HOME"

    UNLOCK_DURATION = "UNLOCK_DURATION"
    CALLS = "CALLS"
    ACTIVITY_TRANSITION = "ACTIVITY_TRANSITION"
    ACTIVITY_RECOGNITION = "ACTIVITY_RECOGNITION"
    AUDIO_LOUDNESS = "AUDIO_LOUDNESS"
    TOTAL_DIST_COVERED = "TOTAL_DIST_COVERED"
    MAX_DIST_TWO_LOCATIONS = "MAX_DIST_TWO_LOCATIONS"
    RADIUS_OF_GYRATION = "RADIUS_OF_GYRATION"
    MAX_DIST_FROM_HOME = "MAX_DIST_FROM_HOME"
    NUM_OF_DIF_PLACES = "NUM_OF_DIF_PLACES"
    GEOFENCE = "GEOFENCE"
    SCREEN_ON_OFF = "SCREEN_ON_OFF"
    APPLICATION_USAGE = "APPLICATION_USAGE"
    SURVEY_EMA = "SURVEY_EMA"

    APP_PCKG_TOCATEGORY_MAP_FILENAME = "package_to_category_map.csv"

    pckg_to_cat_map = {}

    def __init__(self, uid, dataset):
        self.uid = uid
        self.dataset = dataset

    def get_unlock_result(self, dataset, start_time, end_time):
        result = 0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, duration = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time) and number_in_range(int(end), start_time, end_time):
                    result += int(duration)
        return result if result > 0 else "-"

    def get_phonecall_result(self, dataset, start_time, end_time):
        data = list(dataset)
        result = {
            "phone_calls_total_dur": 0,
            "phone_calls_total_number": 0,
            "phone_calls_ratio_in_out": 0
        }

        total_in = 0
        total_out = 0
        if data.__len__() > 0:
            for item in data:
                start, end, call_type, duration = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time) and number_in_range(int(end), start_time, end_time):
                    result["phone_calls_total_dur"] += int(duration)
                    if call_type == "IN":
                        total_in += 1
                    elif call_type == "OUT":
                        total_out += 1

        if result["phone_calls_total_dur"] > 0:
            result["phone_calls_total_number"] = total_in + total_out
            result["phone_calls_ratio_in_out"] = total_in / total_out if total_out > 0 else "-"
        else:
            result["phone_calls_total_dur"] = "-"
            result["phone_calls_total_number"] = "-"
            result["phone_calls_ratio_in_out"] = "-"

        return result

    def get_activities_dur_result(self, dataset, start_time, end_time):

        data = list(dataset)
        result = {
            "still": 0,
            "walking": 0,
            "running": 0,
            "on_bicycle": 0,
            "in_vehicle": 0,
            "on_foot": 0,
            "tilting": 0,
            "unknown": 0
        }

        if data.__len__() > 0:
            for item in data:
                start, end, activity_type, duration = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time) and number_in_range(int(end), start_time, end_time):
                    if activity_type == 'STILL':
                        result['still'] += int(duration)
                    elif activity_type == 'WALKING':
                        result['walking'] += int(duration)
                    elif activity_type == 'RUNNING':
                        result['running'] += int(duration)
                    elif activity_type == 'ON_BICYCLE':
                        result['on_bicycle'] += int(duration)
                    elif activity_type == 'IN_VEHICLE':
                        result['in_vehicle'] += int(duration)
                    elif activity_type == 'ON_FOOT':
                        result['on_foot'] += int(duration)
                    elif activity_type == 'TILTING':
                        result['tilting'] += int(duration)
                    elif activity_type == 'UNKNOWN':
                        result['unknown'] += int(duration)

        if result['still'] == 0:
            result['still'] = "-"
        if result['walking'] == 0:
            result['walking'] = "-"
        if result['running'] == 0:
            result['running'] = "-"
        if result['on_bicycle'] == 0:
            result['on_bicycle'] = "-"
        if result['in_vehicle'] == 0:
            result['in_vehicle'] = "-"
        if result['on_foot'] == 0:
            result['on_foot'] = "-"
        if result['tilting'] == 0:
            result['tilting'] = "-"
        if result['unknown'] == 0:
            result['unknown'] = "-"

        return result

    def get_num_of_dif_activities_result(self, dataset, start_time, end_time):
        data = list(dataset)
        result = {
            "still": 0,
            "walking": 0,
            "running": 0,
            "on_bicycle": 0,
            "in_vehicle": 0,
            "on_foot": 0,
            "tilting": 0,
            "unknown": 0
        }

        if data.__len__() > 0:
            for item in data:
                activity_type, timestamp = item[1].split(" ")
                if number_in_range(int(timestamp), start_time, end_time):
                    if activity_type == 'STILL':
                        result['still'] += 1
                    elif activity_type == 'WALKING':
                        result['walking'] += 1
                    elif activity_type == 'RUNNING':
                        result['running'] += 1
                    elif activity_type == 'ON_BICYCLE':
                        result['on_bicycle'] += 1
                    elif activity_type == 'IN_VEHICLE':
                        result['in_vehicle'] += 1
                    elif activity_type == 'ON_FOOT':
                        result['on_foot'] += 1
                    elif activity_type == 'TILTING':
                        result['tilting'] += 1
                    elif activity_type == 'UNKNOWN':
                        result['unknown'] += 1

        if result['still'] == 0:
            result['still'] = "-"
        if result['walking'] == 0:
            result['walking'] = "-"
        if result['running'] == 0:
            result['running'] = "-"
        if result['on_bicycle'] == 0:
            result['on_bicycle'] = "-"
        if result['in_vehicle'] == 0:
            result['in_vehicle'] = "-"
        if result['on_foot'] == 0:
            result['on_foot'] = "-"
        if result['tilting'] == 0:
            result['tilting'] = "-"
        if result['unknown'] == 0:
            result['unknown'] = "-"

        return result

    def get_audio_data_result(self, dataset, start_time, end_time):
        result = {
            "minimum": 0,
            "maximum": 0,
            "mean": 0
        }

        audio_data = []
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                timestamp, loudness = item[1].split(" ")
                if number_in_range(int(timestamp), start_time, end_time):
                    audio_data.append(float(loudness))

        total_samples = audio_data.__len__()
        result['minimum'] = min(audio_data) if total_samples > 0 else "-"
        result['maximum'] = max(audio_data) if total_samples > 0 else "-"
        result['mean'] = sum(audio_data) / total_samples if total_samples > 0 else "-"

        return result

    def get_total_distance_result(self, dataset, start_time, end_time):
        result = 0.0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, distance = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time):
                    result = float(distance)

        return result if result > 0.0 else "-"

    def get_max_dis_result(self, dataset, start_time, end_time):
        result = 0.0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, distance = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time):
                    result = float(distance)

        return result if result > 0.0 else "-"

    def get_radius_of_gyration_result(self, dataset, start_time, end_time):
        result = 0.0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, value = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time):
                    result = float(value)

        return result if result > 0.0 else "-"

    def get_max_dist_from_home_result(self, dataset, start_time, end_time):
        result = 0.0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, distance = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time):
                    result = float(distance)

        return result if result > 0.0 else "-"

    def get_num_of_places_result(self, dataset, start_time, end_time):
        result = 0.0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, number = item[1].split(" ")
                if number_in_range(int(start), start_time, end_time):
                    result = float(number)

        return result if result > 0.0 else "-"

    def get_time_at_location(self, dataset, start_time, end_time, location_name):
        result = 0
        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                enter_time, exit_time, location_id = item[1].split(" ")
                if number_in_range(int(enter_time), start_time, end_time) and location_id == location_name:
                    result += (int(exit_time) - int(enter_time)) / 1000

        return result if result > 0 else "-"

    def get_unlock_duration_at_location(self, dataset_geofence, dataset_unlock, start_time, end_time, location_name):
        result = 0
        data_geofence = list(dataset_geofence)
        if data_geofence.__len__() > 0:
            for item_geofence in data_geofence:
                enter_time, exit_time, location_id = item_geofence[1].split(" ")
                if number_in_range(int(enter_time), start_time, end_time) and location_id == location_name:
                    data_unlock = list(dataset_unlock)
                    if data_unlock.__len__() > 0:
                        for item_unlock in data_unlock:
                            start, end, duration = item_unlock[1].split(" ")
                            if number_in_range(int(start), int(enter_time), int(exit_time)) and number_in_range(int(end), int(enter_time), int(exit_time)):
                                result += int(duration)

        return result if result > 0 else "-"

    def get_app_category_usage(self, dataset, start_time, end_time):
        result = {
            "Entertainment & Music": 0,
            "Utilities": 0,
            "Shopping": 0,
            "Games & Comics": 0,
            "Others": 0,
            "Health & Wellness": 0,
            "Social & Communication": 0,
            "Education": 0,
            "Travel": 0,
            "Art & Design & Photo": 0,
            "News & Magazine": 0,
            "Food & Drink": 0,
            "Unknown & Background": 0
        }

        data = list(dataset)
        if data.__len__() > 0:
            for item in data:
                start, end, pckg_name = item[1].split(" ")
                duration = (int(end) - int(start)) / 1000
                if number_in_range(int(start), start_time, end_time) and number_in_range(int(end), start_time, end_time):
                    if pckg_name in self.pckg_to_cat_map:
                        category = self.pckg_to_cat_map[pckg_name]
                    else:
                        category = self.get_google_category(pckg_name)
                        self.pckg_to_cat_map[pckg_name] = category

                    if category == "Entertainment & Music":
                        result['Entertainment & Music'] += duration
                    elif category == "Utilities":
                        result['Utilities'] += duration
                    elif category == "Shopping":
                        result['Shopping'] += duration
                    elif category == "Games & Comics":
                        result['Games & Comics'] += duration
                    elif category == "Others":
                        result['Others'] += duration
                    elif category == "Health & Wellness":
                        result['Health & Wellness'] += duration
                    elif category == "Social & Communication":
                        result['Social & Communication'] += duration
                    elif category == "Education":
                        result['Education'] += duration
                    elif category == "Travel":
                        result['Travel'] += duration
                    elif category == "Art & Design & Photo":
                        result['Art & Design & Photo'] += duration
                    elif category == "News & Magazine":
                        result['News & Magazine'] += duration
                    elif category == "Food & Drink":
                        result['Food & Drink'] += duration
                    elif category == "Unknown & Background":
                        result['Unknown & Background'] += duration

        if result['Entertainment & Music'] == 0:
            result['Entertainment & Music'] = "-"
        if result['Utilities'] == 0:
            result['Utilities'] = "-"
        if result['Shopping'] == 0:
            result['Shopping'] = "-"
        if result['Games & Comics'] == 0:
            result['Games & Comics'] = "-"
        if result['Others'] == 0:
            result['Others'] = "-"
        if result['Health & Wellness'] == 0:
            result['Health & Wellness'] = "-"
        if result['Social & Communication'] == 0:
            result['Social & Communication'] = "-"
        if result['Education'] == 0:
            result['Education'] = "-"
        if result['Travel'] == 0:
            result['Travel'] = "-"
        if result['Art & Design & Photo'] == 0:
            result['Art & Design & Photo'] = "-"
        if result['News & Magazine'] == 0:
            result['News & Magazine'] = "-"
        if result['Food & Drink'] == 0:
            result['Food & Drink'] = "-"
        if result['Unknown & Background'] == 0:
            result['Unknown & Background'] = "-"

        return result

    def get_sleep_duration(self, dataset, start_time, end_time):
        result = 0
        durations = []
        data = list(dataset)
        if data.__len__() > 0:
            for index in range(0, len(data)):
                try:
                    cl_start, cl_end, cl_duration = data[index][1].split(" ")
                    nl_start, nl_end, nl_duration = data[index + 1][1].split(" ")

                    if number_in_range(int(cl_start), start_time, end_time):
                        durations.append((int(nl_start) - int(cl_end)) / 1000)
                except IndexError as err:
                    print("Skip this part: ", err)
        if durations:
            result = max(durations)
        return result if result > 0 else "-"

    # audio features during phone calls
    def get_pc_audio_data_result(self, dataset_calls, dataset_audio, start_time, end_time):
        result = {
            "minimum": 0,
            "maximum": 0,
            "mean": 0
        }
        audio_data = []
        data_calls = list(dataset_calls)
        if data_calls.__len__() > 0:
            for index in range(0, len(data_calls)):
                call_start_time, call_end_time, call_type, duration = data_calls[index][1].split(" ")
                if number_in_range(int(call_start_time), start_time, end_time) and number_in_range(int(call_end_time), start_time, end_time):
                    data_audio = list(dataset_audio)
                    for item in data_audio:
                        timestamp, loudness = item[1].split(" ")
                        if number_in_range(int(timestamp), int(call_start_time), int(call_end_time)):
                            audio_data.append(float(loudness))

                    total_audio_samples = audio_data.__len__()
                    result['minimum'] = min(audio_data) if total_audio_samples > 0 else "-"
                    result['maximum'] = max(audio_data) if total_audio_samples > 0 else "-"
                    result['mean'] = sum(audio_data) / total_audio_samples if total_audio_samples > 0 else "-"
        else:
            result['minimum'] = "-"
            result['maximum'] = "-"
            result['mean'] = "-"

        return result

    cat_list = pd.read_csv('Cat_group.csv')

    def get_google_category(self, app_package):
        url = "https://play.google.com/store/apps/details?id=" + app_package
        grouped_Category = ""
        try:
            html = urlopen(url)
            source = html.read()
            html.close()

            soup = BeautifulSoup(source, 'html.parser')
            table = soup.find_all("a", {'itemprop': 'genre'})

            genre = table[0].get_text()

            grouped = self.cat_list[self.cat_list['App Category'] == genre]['Grouped Category'].values
            # print(grouped)

            if len(grouped) > 0:
                grouped_Category = grouped[0]
            else:
                grouped_Category = 'NotMapped'
        except HTTPError as e:
            grouped_Category = 'Unknown or Background'

        finally:
            # print("Pckg: ", App, ";   Category: ", grouped_Category)
            return grouped_Category

    def get_survey_data(self, ema_order, end_time):
        ema_array = list(self.dataset[self.SURVEY_EMA])
        ema_data = []
        if ema_array.__len__() > 0:
            for ema in ema_array:
                answered_time, order, answer1, answer2, answer3, answer4 = ema[1].split(" ")
                if order == ema_order and number_in_range(answered_time, end_time, end_time + self.EMA_RESPONSE_EXPIRE_TIME * 1000):
                    ema_data.append(int(answer1))
                    ema_data.append(int(answer2))
                    ema_data.append(int(answer3))
                    ema_data.append(int(answer4))
        return ema_data

    def extract_regular(self, start_ts, end_ts, ema_order):
        global df
        try:
            columns = ['User id',
                       'Stress lvl',
                       'Responded time',
                       'EMA order',
                       'Unlock duration',
                       'Phonecall duration',
                       'Phonecall number',
                       'Phonecall ratio',
                       'Duration STILL',
                       'Duration WALKING',
                       'Duration RUNNING',
                       'Duration BICYCLE',
                       'Duration VEHICLE',
                       'Duration ON_FOOT',
                       'Duration TILTING',
                       'Duration UNKNOWN',
                       'Freq. STILL',
                       'Freq. WALKING',
                       'Freq. RUNNING',
                       'Freq. BICYCLE',
                       'Freq. VEHICLE',
                       'Freq. ON_FOOT',
                       'Freq. TILTING',
                       'Freq. UNKNOWN',
                       'Audio min.',
                       'Audio max.',
                       'Audio mean',
                       'Total distance',
                       'Num. of places',
                       'Max. distance',
                       'Gyration',
                       'Max. dist.(HOME)',
                       'Duration(HOME)',
                       'Unlock dur.(HOME)',
                       'Entertainment & Music',
                       'Utilities',
                       'Shopping',
                       'Games & Comics',
                       'Others',
                       'Health & Wellness',
                       'Social & Communication',
                       'Education',
                       'Travel',
                       'Art & Design & Photo',
                       'News & Magazine',
                       'Food & Drink',
                       'Unknown & Background',
                       'Sleep dur.',
                       'Phonecall audio min.',
                       'Phonecall audio max.',
                       'Phonecall audio mean']

            print("Processing features for ", self.uid, ".....")

            unlock_data = self.get_unlock_result(self.dataset[self.UNLOCK_DURATION], start_ts, end_ts)
            phonecall_data = self.get_phonecall_result(self.dataset[self.CALLS], start_ts, end_ts)
            activities_total_dur = self.get_activities_dur_result(self.dataset[self.ACTIVITY_TRANSITION], start_ts, end_ts)
            dif_activities = self.get_num_of_dif_activities_result(self.dataset[self.ACTIVITY_RECOGNITION], start_ts, end_ts)
            audio_data = self.get_audio_data_result(self.dataset[self.AUDIO_LOUDNESS], start_ts, end_ts)
            total_dist_data = self.get_total_distance_result(self.dataset[self.TOTAL_DIST_COVERED], start_ts, end_ts)
            max_dist = self.get_max_dis_result(self.dataset[self.MAX_DIST_FROM_HOME], start_ts, end_ts)
            gyration = self.get_radius_of_gyration_result(self.dataset[self.RADIUS_OF_GYRATION], start_ts, end_ts)
            max_home = self.get_max_dist_from_home_result(self.dataset[self.MAX_DIST_FROM_HOME], start_ts, end_ts)
            num_places = self.get_num_of_places_result(self.dataset[self.NUM_OF_DIF_PLACES], start_ts, end_ts)
            time_at = self.get_time_at_location(self.dataset[self.GEOFENCE], start_ts, end_ts, self.LOCATION_HOME)

            unlock_at = self.get_unlock_duration_at_location(
                self.dataset[self.GEOFENCE],
                self.dataset[self.UNLOCK_DURATION],
                start_ts, end_ts, self.LOCATION_HOME)

            pc_audio_data = self.get_pc_audio_data_result(
                self.dataset[self.CALLS],
                self.dataset[self.AUDIO_LOUDNESS],
                start_ts, end_ts)

            app_usage = self.get_app_category_usage(self.dataset[self.APPLICATION_USAGE], start_ts, end_ts)

            day_hour_start = 18
            day_hour_end = 10
            date_start = datetime.datetime.fromtimestamp(end_ts / 1000)
            date_start = date_start - datetime.timedelta(days=1)
            date_start = date_start.replace(hour=day_hour_start, minute=0, second=0)
            date_end = datetime.datetime.fromtimestamp(end_ts / 1000)
            date_end = date_end.replace(hour=day_hour_end, minute=0, second=0)
            # TODO: fix sleep duration computation here
            sleep_duration = self.get_sleep_duration(self.dataset[self.SCREEN_ON_OFF], date_start.timestamp(), date_end.timestamp())

            data = {'User id': self.uid,
                    'Stress lvl': "-",
                    'EMA order': ema_order,
                    'Unlock duration': unlock_data,
                    'Phonecall duration': phonecall_data["phone_calls_total_dur"],
                    'Phonecall number': phonecall_data["phone_calls_total_number"],
                    'Phonecall ratio': phonecall_data["phone_calls_ratio_in_out"],
                    'Duration STILL': activities_total_dur["still"],
                    'Duration WALKING': activities_total_dur["walking"],
                    'Duration RUNNING': activities_total_dur["running"],
                    'Duration BICYCLE': activities_total_dur["on_bicycle"],
                    'Duration VEHICLE': activities_total_dur["in_vehicle"],
                    'Duration ON_FOOT': activities_total_dur["on_foot"],
                    'Duration TILTING': activities_total_dur["tilting"],
                    'Duration UNKNOWN': activities_total_dur["unknown"],
                    'Freq. STILL': dif_activities["still"],
                    'Freq. WALKING': dif_activities["walking"],
                    'Freq. RUNNING': dif_activities["running"],
                    'Freq. BICYCLE': dif_activities["on_bicycle"],
                    'Freq. VEHICLE': dif_activities["in_vehicle"],
                    'Freq. ON_FOOT': dif_activities["on_foot"],
                    'Freq. TILTING': dif_activities["tilting"],
                    'Freq. UNKNOWN': dif_activities["unknown"],
                    'Audio min.': audio_data['minimum'],
                    'Audio max.': audio_data['maximum'],
                    'Audio mean': audio_data['mean'],
                    'Total distance': total_dist_data,
                    'Num. of places': num_places,
                    'Max. distance': max_dist,
                    'Gyration': gyration,
                    'Max. dist.(HOME)': max_home,
                    'Duration(HOME)': time_at,
                    'Unlock dur.(HOME)': unlock_at,
                    'Entertainment & Music': app_usage['Entertainment & Music'],
                    'Utilities': app_usage['Utilities'],
                    'Shopping': app_usage['Shopping'],
                    'Games & Comics': app_usage['Games & Comics'],
                    'Others': app_usage['Others'],
                    'Health & Wellness': app_usage['Health & Wellness'],
                    'Social & Communication': app_usage['Social & Communication'],
                    'Education': app_usage['Education'],
                    'Travel': app_usage['Travel'],
                    'Art & Design & Photo': app_usage['Art & Design & Photo'],
                    'News & Magazine': app_usage['News & Magazine'],
                    'Food & Drink': app_usage['Food & Drink'],
                    'Unknown & Background': app_usage['Unknown & Background'],
                    'Phonecall audio min.': pc_audio_data['minimum'],
                    'Phonecall audio max.': pc_audio_data['maximum'],
                    'Phonecall audio mean': pc_audio_data['mean'],
                    'Sleep dur.': sleep_duration}

            # Finally, save the file here
            df = pd.DataFrame(data, index=[0])
            df = df[columns]
            return df
        except Exception as e:
            print("Ex: ", e)

    def extract_for_after_survey(self):
        global df
        try:
            columns = ['User id',
                       'Stress lvl',
                       'Responded time',
                       'EMA order',
                       'Unlock duration',
                       'Phonecall duration',
                       'Phonecall number',
                       'Phonecall ratio',
                       'Duration STILL',
                       'Duration WALKING',
                       'Duration RUNNING',
                       'Duration BICYCLE',
                       'Duration VEHICLE',
                       'Duration ON_FOOT',
                       'Duration TILTING',
                       'Duration UNKNOWN',
                       'Freq. STILL',
                       'Freq. WALKING',
                       'Freq. RUNNING',
                       'Freq. BICYCLE',
                       'Freq. VEHICLE',
                       'Freq. ON_FOOT',
                       'Freq. TILTING',
                       'Freq. UNKNOWN',
                       'Audio min.',
                       'Audio max.',
                       'Audio mean',
                       'Total distance',
                       'Num. of places',
                       'Max. distance',
                       'Gyration',
                       'Max. dist.(HOME)',
                       'Duration(HOME)',
                       'Unlock dur.(HOME)',
                       'Entertainment & Music',
                       'Utilities',
                       'Shopping',
                       'Games & Comics',
                       'Others',
                       'Health & Wellness',
                       'Social & Communication',
                       'Education',
                       'Travel',
                       'Art & Design & Photo',
                       'News & Magazine',
                       'Food & Drink',
                       'Unknown & Background',
                       'Sleep dur.',
                       'Phonecall audio min.',
                       'Phonecall audio max.',
                       'Phonecall audio mean']

            print("Processing features for ", self.uid, ".....")
            datasets = []

            ema_responses = list(self.dataset[self.SURVEY_EMA])
            if ema_responses.__len__() > 0:
                for index, ema_res in enumerate(ema_responses):
                    print(index + 1, "/", ema_responses.__len__())
                    responded_time, ema_order, a1, a2, a3, a4 = ema_res[1].split(" ")
                    end_time = int(responded_time)
                    start_time = end_time - 4 * 3600 * 1000  # get data 4 hours before each ema
                    if start_time < 0:
                        continue

                    unlock_data = self.get_unlock_result(self.dataset[self.UNLOCK_DURATION], start_time, end_time)
                    phonecall_data = self.get_phonecall_result(self.dataset[self.CALLS], start_time, end_time)
                    activities_total_dur = self.get_activities_dur_result(self.dataset[self.ACTIVITY_TRANSITION], start_time, end_time)
                    dif_activities = self.get_num_of_dif_activities_result(self.dataset[self.ACTIVITY_RECOGNITION], start_time, end_time)
                    audio_data = self.get_audio_data_result(self.dataset[self.AUDIO_LOUDNESS], start_time, end_time)
                    total_dist_data = self.get_total_distance_result(self.dataset[self.TOTAL_DIST_COVERED], start_time, end_time)
                    max_dist = self.get_max_dis_result(self.dataset[self.MAX_DIST_FROM_HOME], start_time, end_time)
                    gyration = self.get_radius_of_gyration_result(self.dataset[self.RADIUS_OF_GYRATION], start_time, end_time)
                    max_home = self.get_max_dist_from_home_result(self.dataset[self.MAX_DIST_FROM_HOME], start_time, end_time)
                    num_places = self.get_num_of_places_result(self.dataset[self.NUM_OF_DIF_PLACES], start_time, end_time)
                    time_at = self.get_time_at_location(self.dataset[self.GEOFENCE], start_time, end_time, self.LOCATION_HOME)

                    unlock_at = self.get_unlock_duration_at_location(
                        self.dataset[self.GEOFENCE],
                        self.dataset[self.UNLOCK_DURATION],
                        start_time, end_time, self.LOCATION_HOME)

                    pc_audio_data = self.get_pc_audio_data_result(
                        self.dataset[self.CALLS],
                        self.dataset[self.AUDIO_LOUDNESS],
                        start_time, end_time)

                    app_usage = self.get_app_category_usage(self.dataset[self.APPLICATION_USAGE], start_time, end_time)

                    day_hour_start = 18
                    day_hour_end = 10
                    date_start = datetime.datetime.fromtimestamp(end_time / 1000)
                    date_start = date_start - datetime.timedelta(days=1)
                    date_start = date_start.replace(hour=day_hour_start, minute=0, second=0)
                    date_end = datetime.datetime.fromtimestamp(end_time / 1000)
                    date_end = date_end.replace(hour=day_hour_end, minute=0, second=0)
                    sleep_duration = self.get_sleep_duration(self.dataset[self.SCREEN_ON_OFF], date_start.timestamp(), date_end.timestamp())

                    data = {'User id': self.uid,
                            'Stress lvl': int(a1) + int(a2) + int(a3) + int(a4),
                            'EMA order': ema_order,
                            'Unlock duration': unlock_data,
                            'Phonecall duration': phonecall_data["phone_calls_total_dur"],
                            'Phonecall number': phonecall_data["phone_calls_total_number"],
                            'Phonecall ratio': phonecall_data["phone_calls_ratio_in_out"],
                            'Duration STILL': activities_total_dur["still"],
                            'Duration WALKING': activities_total_dur["walking"],
                            'Duration RUNNING': activities_total_dur["running"],
                            'Duration BICYCLE': activities_total_dur["on_bicycle"],
                            'Duration VEHICLE': activities_total_dur["in_vehicle"],
                            'Duration ON_FOOT': activities_total_dur["on_foot"],
                            'Duration TILTING': activities_total_dur["tilting"],
                            'Duration UNKNOWN': activities_total_dur["unknown"],
                            'Freq. STILL': dif_activities["still"],
                            'Freq. WALKING': dif_activities["walking"],
                            'Freq. RUNNING': dif_activities["running"],
                            'Freq. BICYCLE': dif_activities["on_bicycle"],
                            'Freq. VEHICLE': dif_activities["in_vehicle"],
                            'Freq. ON_FOOT': dif_activities["on_foot"],
                            'Freq. TILTING': dif_activities["tilting"],
                            'Freq. UNKNOWN': dif_activities["unknown"],
                            'Audio min.': audio_data['minimum'],
                            'Audio max.': audio_data['maximum'],
                            'Audio mean': audio_data['mean'],
                            'Total distance': total_dist_data,
                            'Num. of places': num_places,
                            'Max. distance': max_dist,
                            'Gyration': gyration,
                            'Max. dist.(HOME)': max_home,
                            'Duration(HOME)': time_at,
                            'Unlock dur.(HOME)': unlock_at,
                            'Entertainment & Music': app_usage['Entertainment & Music'],
                            'Utilities': app_usage['Utilities'],
                            'Shopping': app_usage['Shopping'],
                            'Games & Comics': app_usage['Games & Comics'],
                            'Others': app_usage['Others'],
                            'Health & Wellness': app_usage['Health & Wellness'],
                            'Social & Communication': app_usage['Social & Communication'],
                            'Education': app_usage['Education'],
                            'Travel': app_usage['Travel'],
                            'Art & Design & Photo': app_usage['Art & Design & Photo'],
                            'News & Magazine': app_usage['News & Magazine'],
                            'Food & Drink': app_usage['Food & Drink'],
                            'Unknown & Background': app_usage['Unknown & Background'],
                            'Phonecall audio min.': pc_audio_data['minimum'],
                            'Phonecall audio max.': pc_audio_data['maximum'],
                            'Phonecall audio mean': pc_audio_data['mean'],
                            'Sleep dur.': sleep_duration}

                    datasets.append(data)  # dataset of rows

            # Finally, save the file here
            for dataset in datasets:
                df = pd.DataFrame(dataset, index=[0])
                df = df[columns]
            return df
        except Exception as e:
            print("Ex: ", e)
