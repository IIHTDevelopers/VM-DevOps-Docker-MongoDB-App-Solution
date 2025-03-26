def create_hello_file():
    """Creates a text file and saves the word 'Hello' in it."""
    try:
        with open('hello.txt', 'w') as file:
            file.write('Hello')
        print("File 'hello.txt' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_hello_file()
