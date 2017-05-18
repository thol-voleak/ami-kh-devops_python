
import subprocess


def get_app_and_migration(line):
    """
    Get app name and migration name from line like this
    [X] contenttypes.0001_initial
    """
    text = line.split()[2]
    return text.split(".")


def run_command_and_get_output(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')


def generate_sql():
    cmd = 'python manage.py showmigrations --plan'.split()
    migrations = run_command_and_get_output(cmd)
    migrations = filter(lambda x: x.strip(), migrations.split("\n"))
    migrations = map(get_app_and_migration, migrations)
    sql_script = ''
    for app_name, migration_number in migrations:
        command = 'python manage.py sqlmigrate {app_name} {migration_number}'.format(
            app_name=app_name,
            migration_number=migration_number,
        )
        sql_script += run_command_and_get_output(command.split())
        sql_script += "\n"

    with open('sql_script.sql', 'w+') as f:
        f.write(sql_script)


if __name__ == "__main__":
    generate_sql()
