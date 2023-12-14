import os
import stat
import click


def load_properties(filepath, sep='=', comment_char='#'):
    """
    Read the file passed as parameter as a properties file.
    """
    props = {}
    with open(filepath, "rt") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"')
                props[key] = value
    return props


def get_gradle_version(properties_file):
    properties_content = load_properties(properties_file)
    distribution_url = properties_content.get("distributionUrl")
    all_strings = distribution_url.split("/")
    last_string = all_strings[-1]
    version_strings = last_string.split("-")
    version = version_strings[1]
    gradle_version = int(version.replace(".", ""))
    if gradle_version < 100:
        gradle_version = gradle_version * 10
    return gradle_version


def rename_gradlew_to_gradlew_origin(file_path):
    src_file = file_path
    dest_file = file_path.replace("/gradlew", "/gradlew-origin")
    os.rename(src_file, dest_file)
    make_file_executable(dest_file)


def create_new_gradlew(file_path):
    with open(file_path, "w") as gradlew_file:
        gradlew_file.write("""#!/bin/bash
  echo $@
  i=1
  arg_str=""

  for arg in "$@"; do
    if [ $arg != "--no-parallel" ]; then
      arg_str="$arg_str $arg"
    fi
    i=$((i + 1))
  done
  echo workaround - call original gradlew with arguments: $arg_str
  bash gradlew-origin $arg_str
""")


def make_file_executable(file_path):
    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)


@click.command()
@click.argument('path')
def main(path):
    for (root, dirs, files) in os.walk(path):
        if 'gradlew' not in files:
            continue
        gradlew_file_path = root + "/gradlew"
        gradle_wrapper_properties = root + "/gradle/wrapper/gradle-wrapper.properties"
        gradle_version = get_gradle_version(gradle_wrapper_properties)
        if gradle_version <= 430:
            rename_gradlew_to_gradlew_origin(gradlew_file_path)
            create_new_gradlew(gradlew_file_path)
            make_file_executable(gradlew_file_path)
        print(f"root: {root}")
        print(f"dirs: {dirs}")
        print(f"files: {files}")


if __name__ == '__main__':
    main()
