import xml.etree.ElementTree as ET
from os import getcwd

sets=[('2007', 'train'), ('2007', 'val'), ('2007', 'test')]

classes = ['bird', 'pipe']


def convert_annotation(image_id, list_file):
    in_file = open('Annotations/%s.xml'%(image_id))
    tree=ET.parse(in_file)
    root = tree.getroot()

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))

wd = getcwd()

image_ids = open('ImageSets/Main/train.txt').read().strip().split()
list_file = open('bird_train.txt', 'w')
for image_id in image_ids:
    list_file.write('%s\\JPGs\\%s.jpg'%(wd, image_id))
    convert_annotation(image_id, list_file)
    list_file.write('\n')
list_file.close()

image_ids = open('ImageSets/Main/test.txt').read().strip().split()
list_file = open('bird_test.txt', 'w')
for image_id in image_ids:
    list_file.write('%s\\JPGs\\%s.jpg'%(wd, image_id))
    # newid = '{0:>6}'.format(str(int(image_id)-1))
    convert_annotation(image_id, list_file)
    list_file.write('\n')
list_file.close()