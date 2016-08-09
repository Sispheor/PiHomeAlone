from flask import jsonify
import threading
from flask import request
from flask_restful import abort


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
        self.app.add_url_rule('/', view_func=self.post_alarm_status, methods=['PUT'])

    def run(self):
        self.app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)

    def get_alarm_status(self):
        """
        get the current alarm status
        """
        data = {
            "alarm_status": self.main_thread.status,
            "siren_status": self.main_thread.arduino.get_siren_status()
        }
        return jsonify(data), 200

    def post_alarm_status(self):
        """
        Update the alarm
        """
        # get data from the request
        if not request.json or not 'alarm_status' in request.json or not 'siren_status' in request.json:
            abort(400)

        # check data
        new_alarm_status = request.json['alarm_status']
        new_siren_status = request.json['siren_status']
        if new_alarm_status not in ["enabled", "disabled"] or new_siren_status not in ["on", "off"]:
            abort(400)

        # if we are here, no error 400, we can call the main thread to update the system
        self.main_thread.update_status(new_alarm_status, new_siren_status)

        data = {
            "alarm_status": new_alarm_status,
            "siren_status": new_siren_status
        }

        return jsonify(data), 201
