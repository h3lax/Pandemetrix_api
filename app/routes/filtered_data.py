from flask_restx import Namespace, Resource, reqparse
from app.etl.components.mongodb import fetch_data
from config import Config
from datetime import datetime
import json


filtered_data_ns = Namespace("data", description="Filtered Data Operations")

parser = reqparse.RequestParser()
parser.add_argument("country", type=str, required=False, help="Country filter")
parser.add_argument("start_date", type=str, required=False, help="Start date (YYYY-MM-DD)")
parser.add_argument("end_date", type=str, required=False, help="End date (YYYY-MM-DD)")
parser.add_argument("page", type=int, default=1, help="Page number")
parser.add_argument("page_size", type=int, default=1000, help="Number of documents per page")

@filtered_data_ns.route("/")
class FilteredData(Resource):
    @filtered_data_ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        country = args.get("country")
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        page = args.get("page")
        page_size = args.get("page_size")
        skip = (page - 1) * page_size
        
        # Build the MongoDB filter
        query = {}
        if country:
            query['country'] = country
        
        # Date filtering
        date_filter = {}
        if start_date:
            try:
                date_filter['$gte'] = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return {"error": "Invalid start date format. Use YYYY-MM-DD."}, 400
        if end_date:
            try:
                date_filter['$lte'] = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return {"error": "Invalid end date format. Use YYYY-MM-DD."}, 400
        
        if date_filter:
            query['date'] = date_filter
        
        # Fetch data
        try:
            # This is now correctly serialized
            data = fetch_data(Config.MONGODB_CONFIG, "test", query, skip=skip, limit=page_size)
            return json.loads(data), 200
        except Exception as e:
            return {"error": str(e)}, 500