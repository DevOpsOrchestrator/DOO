

def handle_uploaded_file(file, path):
    with open(path+file.name, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
