import os
import connexion
from flask_cors import CORS

# Create the application instance
app = connexion.App(__name__, specification_dir='/openapi/')

# Add CORS support
CORS(app.app)

# Read the OpenAPI specification
app.add_api('openapi.yml', resolver=connexion.resolver.RelativeResolver('api'))

# Create a URL route for the home page
@app.route('/')
def home():
    return {'message': 'Welcome to the API server!'}

# Start the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 