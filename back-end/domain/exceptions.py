class PageNotFoundError(Exception):
    def __init__(self):
        super().__init__("Couldn't find next offers page")


class OfferLinkAlreadyInDatabaseError(Exception):
    def __init__(self):
        super().__init__("Offer link is already in the database")


class StageFailedError(Exception):
    def __init__(self):
        super().__init__("Stage failed")