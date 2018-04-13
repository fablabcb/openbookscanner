# Install Sane
# from https://www.cyberciti.biz/faq/linux-scan-image-commands/
sudo apt-get install sane sane-utils

# Install simple scan
# from https://www.linuxquestions.org/questions/linux-hardware-18/scanning-using-scanner-canon-lide-120-canon-with-sane-4175609129/
sudo apt-get install simple-scan

# Install imagemagick to convert images
# from http://dev-random.net/convert-multiple-jpg-or-png-to-pdf-in-linux/
# this provides the "convert" command
sudo apt-get install ghostscript imagemagick

echo "In order to scan, please reboot"
echo "sudo reboot"
