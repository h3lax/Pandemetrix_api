from flask import request
from flask_restx import Namespace, Resource
import pandas as pd
from app.etl.components.transform import transform_data
from app.etl.components.mongodb import insert_data, get_collection_infos
from app.etl.main import get_url, download_csv
from config import Config
import io

etl_ns = Namespace('etl', description='ETL operations')

@etl_ns.route('/upload')
class FileUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'No file part in the request'}, 400
        
        file = request.files['file']
        title = request.form.get('title', 'default')
        
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        try:
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            transformed = transform_data(df)

            if transformed.empty:
                return {'message': 'No data after transformation'}, 400

            insert_data(transformed, title)
            return {'message': 'File uploaded and processed successfully'}, 200
        except Exception as e:
            return {'message': f'Error processing file: {str(e)}'}, 500

@etl_ns.route('/download')
class FileDownload(Resource):
    def post(self):
        code = request.json.get('code')
        if not code:
            return {'message': 'Code is required'}, 400
        
        try:
            url = get_url(code)
            if not url:
                exit()
            csv_content = download_csv(url)
            raw_data = pd.read_csv(io.StringIO(csv_content))
            transformed = transform_data(raw_data)

            if transformed.empty:
                return {'message': 'No data after transformation'}, 400

            insert_data(transformed, "TESTURLE")
            return {'message': 'File uploaded and processed successfully'}, 200
        except Exception as e:
            return {'message': f'Error processing file: {str(e)}'}, 500

@etl_ns.route('/collections')
class GetCollections(Resource):
    def get(self):
        try:
            collections = get_collection_infos()
            return {'collections': collections, 'message': 'Collections fetched successfully'}, 200
        except Exception as e:
            return {'message': f'Error fetching collections: {str(e)}'}, 500
        