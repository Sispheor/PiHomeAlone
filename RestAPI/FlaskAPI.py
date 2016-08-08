from flask import jsonify
import threading

from flask.views import MethodView


class AlarmAPI(MethodView):

    def get(self):
        """
        get the current alarm status
        """
        data = {
            "alarm_status": "test",
            "siren_status": "test3"
        }
        return jsonify(data)

    def put(self, user_id):
        # update the alamr status
        pass


class FlaskAPI(threading.Thread):
    def __init__(self, app, shared_queue_message_from_api):
        super(FlaskAPI, self).__init__()
        print "Run Flask Rest API"
        self.shared_queue_message_from_api = shared_queue_message_from_api
        self.app = app
        alarm_view = AlarmAPI.as_view('user_api')
        self.app.add_url_rule('/', view_func=alarm_view, methods=['GET', 'PUT'])

    def run(self):
        self.app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)


