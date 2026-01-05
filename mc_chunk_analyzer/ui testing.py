# import ttkbootstrap as ttk
# from presentation.Widgets import ConsoleWidget, PathWidget, DimensionSelector
# from pathlib import Path
#
# root = ttk.Window(themename="darkly", size=(1000,720))
# path = PathWidget(root,lambda a: print(a.parts))
# path.pack()
#
# dim = DimensionSelector(root)
# # dim.pack()
#
#
#
# console = ConsoleWidget(root, "cool console bro")
# console.pack()
# console.log("err", "error")
# console.log("something happened")
# root.mainloop()
#


a = [2310355422147575936, 2310355422147575936, 2310355422147575936,
 2310355422147575936, 2310355422147575936, 2310355422147575936,
 2310355422147575936, 2310355422147575936, 2310355422147575936,
 2310355422147575936, 2310355422147575936, 2310355422147575936]

# curr = 0
# max_curr = len(a) * 64
# while 1:
#     word_index = curr // 64
#     bit_index = curr % 64
#
#     curr += 9
#     if curr > max_curr: break
#
#     if bit_index + 9 < 64:
#         print(bin(a[word_index] >> (64 - bit_index - 9)), len(bin(a[word_index] >> (64 - bit_index - 9))))
#         print((a[word_index] >> (64 - bit_index - 9)) & 0b111111111)
#         exit()



# print(f'{2310355422147575936:064b}', f'{2310355422147575936:064b}')
num = 2310355422147575936
a = ( num >> 54) & 0b111111111
print(f'{num >> 54:064b}')
print(a)
# print(num << 1 & 0b111111111)