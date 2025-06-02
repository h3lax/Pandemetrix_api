from flask import request
from flask_restx import Namespace, Resource
import pandas as pd
from app.etl.components.transform import transform_data
from app.etl.components.mongodb import insert_data
from config import Config
import io


etl_ns = Namespace('etl', description='ETL operations')

@etl_ns.route('/upload')
class FileUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'No file part in the request'}, 400
        
        file = request.files['file']
        
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        try:
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            transformed = transform_data(df)

            if transformed.empty:
                return {'message': 'No data after transformation'}, 400

            insert_data(Config.MONGODB_CONFIG, transformed, 'SALUTANTHONY')
            return {'message': 'File uploaded and processed successfully'}, 200
        except Exception as e:
            return {'message': f'Error processing file: {str(e)}'}, 500