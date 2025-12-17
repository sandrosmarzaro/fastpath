from fastapi.openapi.models import Example

UserExample: dict[str, Example] = {
    'normal': {
        'summary': 'A test example',
        'description': 'A **test** user works correctly.',
        'value': {
            'username': 'fulano',
            'email': 'fulano@email.com',
            'password': 'P4ssw@rd',
        },
    },
}
