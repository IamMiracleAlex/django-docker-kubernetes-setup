from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
	location = 'static'
	default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
	location = 'media'
	default_acl = 'public-read'
	file_overwrite = True


class ImportExportStorage(S3Boto3Storage):
	location = 'import_export'
	default_acl = 'public-read'
	file_overwrite = False



class FileStorage(FileSystemStorage):
	file_overwrite = True
