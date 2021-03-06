from flask import send_file, safe_join
from flask_restplus import Namespace, Resource, reqparse
from flask_login import login_required, current_user

import datetime
from ..util import query_util

from database import (
    ExportModel,
    DatasetModel,
    fix_ids
)


api = Namespace('export', description='Export related operations')


@api.route('/<int:export_id>')
class DatasetExports(Resource):
    @login_required
    def get(self, export_id):
        """ Returns exports """
        export = ExportModel.objects(id=export_id).first()
        if export is None:
            return {"message": "Invalid export ID"}, 400

        dataset = current_user.datasets.filter(id=export.dataset_id).first()
        if dataset is None:
            return {"message": "Invalid dataset ID"}, 400
        
        time_delta = datetime.datetime.utcnow() - export.created_at
        d = fix_ids(export)
        d['ago'] = query_util.td_format(time_delta)
        return d
    
    @login_required
    def delete(self, export_id):
        """ Returns exports """
        export = ExportModel.objects(id=export_id).first()
        if export is None:
            return {"message": "Invalid export ID"}, 400

        dataset = current_user.datasets.filter(id=export.dataset_id).first()
        if dataset is None:
            return {"message": "Invalid dataset ID"}, 400
        
        export.delete()
        export.remove_zip_file()
        return {'success': True}


@api.route('/<int:export_id>/download')
class DatasetExports(Resource):
    @login_required
    def get(self, export_id):
        """ Returns exports """
        export = ExportModel.objects(id=export_id).first()
        if export is None:
            return {"message": "Invalid export ID"}, 400

        dataset = current_user.datasets.filter(id=export.dataset_id).first()
        if dataset is None:
            return {"message": "Invalid dataset ID"}, 400
        
        if not current_user.can_download(dataset):
            return {"message": "You do not have permission to download the dataset's annotations"}, 403

        safe_path = safe_join('/workspace', export.path)
        return send_file(safe_path, as_attachment=True)

