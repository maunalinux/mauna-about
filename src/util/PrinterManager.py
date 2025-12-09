import cups


def get_printers():
    conn = cups.Connection()
    printers = conn.getPrinters()

    printers_list = []
    for p in printers:
        printer_obj = {
            "name": p,
            # "device-uri": printers[p]["device-uri"],
            # "printer-uri": printers[p]["printer-uri-supported"],
            "info": printers[p]["printer-make-and-model"],
        }

        printers_list.append(printer_obj)

    return printers_list


print(get_printers())
