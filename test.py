import streamlit as st
from PIL import Image
from pyzbar.pyzbar import decode
import sqlite3

# SQLite setup
conn = sqlite3.connect('scanprods.db')
c = conn.cursor()

# Function to scan QR code from image
def scan_qr_code_from_image(img):
    img_gray = img.convert('L')
    decoded_objects = decode(img_gray)
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')
        return qr_data
    else:
        return None

# Function to fetch product details from database using product ID
def fetch_product_details(product_id):
    c.execute('SELECT product_name, barcode, expiry_date, status FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()
    if product:
        return product
    else:
        return None

def main():
    st.title('Product QR Code Scanner')
    st.write("Choose how you'd like to scan the QR code:")

    option = st.selectbox(
        '',
        ('Upload Image', 'Scan with Mobile QR App')
    )

    if option == 'Upload Image':
        uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            qr_data = scan_qr_code_from_image(img)
            if qr_data:
                if qr_data.startswith('PRODAPP:'):
                    try:
                        product_id = int(qr_data.split('\n')[0].split(': ')[1])
                        product_details = fetch_product_details(product_id)
                        if product_details:
                            product_name, barcode, expiry_date, status = product_details
                            st.success(f"Decoded QR Code Data:")
                            st.write(f"Product Name: {product_name}")
                            st.write(f"Barcode: {barcode}")
                            st.write(f"Expiry Date: {expiry_date}")
                            st.write(f"Status: {status}")

                            if status == 'AUTHORIZED':
                                st.success('Product is Authorized')
                                if st.button('Buy Product'):
                                    st.write('Product purchased successfully!')
                            else:
                                st.warning('Product is not Authorized')
                        else:
                            st.warning("Product details not found.")
                    except Exception as e:
                        st.warning("Error decoding QR code data.")
                        st.warning(f"Details: {e}")
                else:
                    st.warning("This QR code was not generated by PRODAPP.")
            else:
                st.warning("No QR code found in the uploaded image.")

    elif option == 'Scan with Mobile QR App':
        st.write("Please use your mobile device's QR scanning app and scan the QR code.")
        st.write("Ensure your device's camera focuses properly on the QR code.")
        st.write("The QR code should start with 'PRODAPP:'")

if __name__ == '__main__':
    main()
