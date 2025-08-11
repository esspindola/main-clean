class User:
    def __init__(self, id, email, fullName, role, phone=None, address=None):
        self.id = id
        self.email = email
        self.fullName = fullName
        self.role = role
        self.phone = phone
        self.address = address