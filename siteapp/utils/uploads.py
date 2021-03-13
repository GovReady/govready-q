def hash_file(file, block_size=65536):
    import hashlib
    hasher = hashlib.sha512()
    from functools import partial
    for buf in iter(partial(file.read, block_size), b''):
        hasher.update(buf)

    return hasher.hexdigest()
