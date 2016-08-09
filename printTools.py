import cups

def print_file(filename):
	printer = get_active_printer()
	if printer == None:
		print "No Active Printer"
		return
	options = {}
	options['media'] = 'Letter'
	options['fit-to-page'] = 'True'
	cups.Connection().printFile(printer, filename, 'NYT_PRINT', options)


def get_active_printer():
	conn = cups.Connection()
	default_printer = conn.getDefault()
	printers = conn.getPrinters()

	active_printer = None
	for printer in printers:
		if printers[printer]['printer-state'] == 3:
			if printer == default_printer:
				return default_printer
			active_printer = printer
	return active_printer