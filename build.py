import tarfile
import hashlib
import sys
import os.path

from pynt import task

@task()
def release(version = None):
    """Creates a release archive."""

    if not version:
        print('No version specified. Aborting...')
        return False

    hash_ver = hashlib.sha256()

    # snippet adapted from:
    #    https://www.pythoncentral.io/hashing-files-with-python/
    with open('bot.py', 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hash_ver.update(buf)
            buf = f.read(65536)

    # not using this for security purposes anyway. only for versioning.
    hash_ver = hash_ver.hexdigest()[-5:]

    tar_name = 'wings_of_vaivora-v.{}-{}.tar.gz'.format(version,
                                                        hash_ver)

    tar = tarfile.open(tar_name, 'w:gz')

    tar.add('bot.py')
    tar.add('cogs')
    tar.add('vaivora')
    tar.add('constants')
    tar.add('utils')
    tar.add('secrets.py.example')
    tar.add('checks.py')
    tar.add('build.py')
    tar.add('requirements.txt')
    tar.add('README.md')
    tar.add('disclaimer.py')
    tar.add('docs')
    tar.add('LICENSE')
    tar.add('LICENSES')

    tar.close()


@task()
def configure():
    """Configures the package for use."""

    if not os.path.isdir('db'):
        try:
            print('Attempting to create missing db directory...')
            os.mkdir('db')
            print('Success! db was created.')
        except:
            try:
                print('Encountered existing file. Attempting to remove...')
                os.remove('db')
                os.mkdir('db')
                print('Success! db was created.')
            except:
                print('Could not remove invalid file db!  Exiting...')
                sys.exit(1)
    else:
        print('Directory db already created. Continuing...')

    try:
        token = input('Enter your bot token: ')
    except:
        print('Token not entered. Exiting...')
        sys.exit(1)

    try:
        uid = input('(optional) Enter your own Discord ID: ')
        uid = int(uid)
    except KeyboardInterrupt:
        print('User ID not entered. Ignoring...')
        uid = 0
    except:
        print('Invalid ID entered. Exiting...')
        sys.exit(1)

    print('Writing to secrets.py')

    with open('secrets.py.example', 'r') as f:
        secrets = f.read()

    secrets = secrets.format(uid, token)

    with open('secrets.py', 'w') as f:
        f.write(secrets)

    print('Success! secrets.py has been set up.')

    print('Configuration complete.')


__DEFAULT__ = configure