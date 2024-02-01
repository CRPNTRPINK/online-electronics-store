def generate_string(min_length, max_length, faker):
    result = faker.text(max_nb_chars=max_length)
    while len(result) < min_length:
        result += faker.text(max_nb_chars=max_length - len(result))
    return result[:max_length]
