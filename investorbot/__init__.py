from investorbot.interfaces.services import ICryptoService
from investorbot.services import AppService, SmtpService
from investorbot.integrations.cryptodotcom.services import CryptoService

crypto_service: ICryptoService = CryptoService()
app_service = AppService()
smtp_service = SmtpService()
