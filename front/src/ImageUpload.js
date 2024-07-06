import React, { useState } from 'react';
import './App.css';

const ImageUpload = () => {
    const [selectedImage, setSelectedImage] = useState(null);
    const [uploadMessage, setUploadMessage] = useState('');
    const [modelResponse, setModelResponse] = useState([]);

    const handleImageChange = (event) => {
        setSelectedImage(event.target.files[0]);
    };

    const handleImageUpload = async () => {
        if (!selectedImage) {
            setUploadMessage('Please select an image to upload.');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', selectedImage);

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/execute`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Image upload failed: ${response.statusText}`);
            }

            const data = await response.json();

            setModelResponse(data.images || []);
            setUploadMessage('Image uploaded and processed successfully.');
        } catch (error) {
            console.error('There has been a problem with your fetch operation:', error);
            setUploadMessage(`Error: ${error.message}`);
        }
    };

    return (
        <div className="App">
            <header>
                <h2>TelICU Patient Monitoring System</h2>
            </header>
            <input type="file" id="file" onChange={handleImageChange} />
            <label htmlFor="file" className="label-file">Choose Image</label>
            <button className="button-upload" onClick={handleImageUpload}>Upload Image</button>
            {uploadMessage && <p className="message">{uploadMessage}</p>}
            <div className="image-results">
                {modelResponse.map((image, index) => (
                    <img key={index} src={image} alt={`Processed ${index}`} />
                ))}
            </div>
        </div>
    );
};
export default ImageUpload;
