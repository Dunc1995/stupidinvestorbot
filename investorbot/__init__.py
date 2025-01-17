from investorbot.interfaces.services import ICryptoService
from investorbot.services import CryptoService, AppService, SmtpService

crypto_service: ICryptoService = CryptoService()
app_service = AppService()
smtp_service = SmtpService()
