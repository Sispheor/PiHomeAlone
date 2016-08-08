from flask import jsonify
import threading


class FlaskAPI(threading.Thread):
    def __init__(self, app, shared_queue_message_from_api):
        super(FlaskAPI, self).__init__()
        print "Run Flask Rest API"
        self.shared_queue_message_from_api = shared_queue_message_from_api
        self.app = app
        self.app.add_url_rule('/', view_func=self.get_alarm)

    def run(self):
        self.app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)

    def get_alarm(self):
        """
        Get the current status of the alarm
        :return:
        """
        print "send message"
        self.shared_queue_message_from_api.put("coucou")

        data = {
            "alarm_status": "test",
            "siren_status": "test2"
        }
        return jsonify(data)

