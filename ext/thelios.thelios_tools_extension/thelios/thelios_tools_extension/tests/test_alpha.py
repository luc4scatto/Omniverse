from PIL import Image

img_path = r"C:\Users\l.scattolin\Desktop\CD40153U_32P_frames\CD40153U_32P.01.png"

img = Image.open(img_path).convert('RGBA')
datas = img.getdata()

new_data = []
for item in datas:
    # item è (R,G,B,A). Considera "quasi bianco" anche valori non esattamente 255
    if item[0] > 255 and item[1] > 255 and item[2] > 255:
        # Trasforma pixel quasi bianco in trasparente
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)

img.putdata(new_data)
img.save(r"C:\Users\l.scattolin\Desktop\CD40153U_32P_frames\output_scontornato.png")
