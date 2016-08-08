from flask import jsonify
import threading


class FlaskAPI(threading.Thread):
    def __init__(self, app, shared_queue_message_from_api, mainthread):
        super(FlaskAPI, self).__init__()
        print "Run Flask Rest API"
        self.shared_queue_message_from_api = shared_queue_message_from_api
        self.app = app
        # the main controller object
        self.main_thread = mainthread
        # alarm_view = AlarmAPI.as_view('user_api')
        self.app.add_url_rule('/', view_func=self.get_alarm_status, methods=['GET'])
        self.app.add_url_rule('/', view_func=self.post_alarm_status, methods=['POST'])

    def run(self):
        self.app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)

    def get_alarm_status(self):
        """
        get the current alarm status
        """
        data = {
            "alarm_status": self.main_thread.status,
            "siren_status": "off"
        }
        return jsonify(data)

    def post_alarm_status(self):
        """
        get the current alarm status
        """

        self.main_thread.enable_system()
        data = {
            "alarm_status": self.main_thread.status,
            "siren_status": "off"
        }

        return jsonify(data)