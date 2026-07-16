from app.services.preprocessing_service import PreprocessingService

service = PreprocessingService()

result = service.run()

print(result)