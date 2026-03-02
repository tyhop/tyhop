from flask import Flask
from flask_cors import CORS

from com.tgu.routes.init import api_v1

app = Flask(__name__)
CORS(app)
# 注册APIv1蓝图
app.register_blueprint(api_v1)


@app.route('/')
def index():
    return {
        'message': '航班行李安检系统API',
        'version': '1.0.0',
        'documentation': '/api/docs',
        'endpoints': {
            'auth': '/api/auth',
            'users': '/api/users',
            'travellers': '/api/travellers',
            'baggage': '/api/baggage',
            'flights': '/api/flights',
            'system': '/api/system'
        }
    }


if __name__ == "__main__":
    app.run()
