import sys
import os


# Tag declaration
del_tag = "\\del{"
add_tag = "\\add{"
input_tag = "\\input{"


def remove_del(line):
	if del_tag not in line:
		return line

	s = ""
	open_bracket = -1
	stack = []
	i = 0
	is_comment = False
	while i < len(line):
		if line[i] == "%" and not (i > 0 and line[i-1] == "\\"):
			is_comment = True

		if line[i] == "\n":
			is_comment = False

		if is_comment:
			s += line[i]
			i += 1
			continue

		if i < len(line) - len(del_tag) and line[i:i+5] == del_tag and open_bracket == -1:
			stack.append(i+5)
			open_bracket = len(stack)
			i += 6
			continue

		if line[i] == "}":
			if len(stack) == open_bracket:
				stack.pop()
				open_bracket = -1
				i += 1
			else:
				stack.pop()
		elif line[i] == "{":
			stack.append(i)

		if open_bracket == -1:
			s += line[i]
			if len(s) > 1 and s[-2:] == "  ":
				s = s[:-1]

		i += 1
	return s


def remove_add(line):
	if add_tag not in line:
		return line
	
	s = ""
	open_bracket = -1
	stack = []
	i = 0
	is_comment = False
	while i < len(line):
		if line[i] == "%" and not (i > 0 and line[i-1] == "\\"):
			is_comment = True

		if line[i] == "\n":
			is_comment = False

		if is_comment:
			s += line[i]
			i += 1
			continue

		if i < len(line) - len(add_tag) and line[i:i+5] == add_tag and open_bracket == -1:
			stack.append(i+5)
			open_bracket = len(stack)
			i += 5
			continue

		if line[i] == "}":
			if len(stack) == open_bracket:
				stack.pop()
				open_bracket = -1
				i += 1
			else:
				stack.pop()
		elif line[i] == "{":
			stack.append(i)

		s += line[i]
		i += 1
	return s


def get_all_files(main_file):
	abspath = os.path.dirname(os.path.abspath(main_file))
	res = set()
	res.add(main_file)
	with open(main_file, 'r') as f:
		for line in f:
			if input_tag in line:
				i = 0
				open_bracket = -1
				is_comment = False
				while i < len(line):
					if line[i] == "%" and not (i > 0 and line[i-1] == "\\"):
						is_comment = True
					if line[i] == "\n":
						is_comment = False
					if is_comment:
						i += 1
						continue

					if i < len(line) - len(input_tag) and line[i:i+len(input_tag)] == input_tag:
						open_bracket = i+len(input_tag)
						i += len(input_tag)
					elif line[i] == "}" and input_tag != -1:
						filename = line[open_bracket:i]
						filepath = os.path.join(abspath,filename)
						if os.path.isfile(filepath):
							res.add(filepath)
							res |= get_all_files(filepath)
						open_bracket = -1
					i += 1
	return res


def remove_tags(filepath):
	print("Removing tags for {}".format(filepath))
	filename, file_extension = os.path.splitext(filepath)
	filepath_out = filename+'_out'+file_extension
	with open(filepath_out, 'w') as f_out:
		with open(filepath, 'r') as f:
			l = ""
			for line in f:
				if line == '\n':
					l = remove_add(remove_del(l))
					f_out.write(l)
					l = ""
				l += line
			
			l = remove_add(remove_del(l))
			f_out.write(l)

	os.rename(filepath_out, filepath)



if __name__ == '__main__':
	filepath = sys.argv[1]
	files = get_all_files(filepath)
	for f in files:
		remove_tags(f)
		print("Done for {}".format(f))

