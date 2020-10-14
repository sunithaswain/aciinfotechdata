from dependency_injector import providers, containers


class Configs(containers.DeclarativeContainer):

    from app.utility.config import Configuration
    config = providers.Singleton(Configuration)


class DataProviders(containers.DeclarativeContainer):

    from app.providers.db_queries import QueryExecutor
    dataqueriesprovider = providers.Factory(QueryExecutor, Configs.config)

    from app.providers.claim_portal_provider import ClaimPortalProvider
    claimportaldataprovider = providers.Factory(
        ClaimPortalProvider, Configs.config)


class Models(containers.DeclarativeContainer):

    from app.models.claim import Claim
    claimmodel = providers.Factory(Claim)



class Service(containers.DeclarativeContainer):
    from app.service.claim_portal_service import ClaimPortalProcessor
    portal_service = providers.Factory(ClaimPortalProcessor, config=Configs.config, claimobj=Models.claimmodel,
                                       claimportaldataprovobj=DataProviders.claimportaldataprovider)

class Utilities(containers.DeclarativeContainer):

    from app.utility.error_email_notifier import EmailNotificationHandler
    emailnotif = providers.Factory(EmailNotificationHandler)

    from app.utility.sendgridemail import SendgridEmail
    sendemail = providers.Factory(SendgridEmail)
