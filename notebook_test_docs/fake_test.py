from faker import Faker

fake = Faker('en_UK')

print(fake.pystr(max_chars=100))
