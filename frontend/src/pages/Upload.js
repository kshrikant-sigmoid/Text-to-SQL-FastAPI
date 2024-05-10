import React, { useState, useEffect } from 'react';
import axios from '../services/axiosConfig';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState(false);

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
    setUploadSuccess(false);
    setUploadError(false);
  };

  const onFileUpload = async () => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.status === 200) {
        setUploadSuccess(true);
        setUploadError(false);
      } else {
        setUploadError(true);
        setUploadSuccess(false);
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setUploadError(true);
      setUploadSuccess(false);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 text-center">
          <h1 className='font-bold' style={{ textAlign: 'center', fontSize: '25px', marginBottom: '20px' }}>File Upload</h1>

      <input type="file" onChange={onFileChange} className="border border-gray-300 rounded-md px-4 py-2 mb-4" />
      <button onClick={onFileUpload} className="bg-pink-400 hover:bg-pink-500 text-white font-bold py-2 px-4 rounded" style={{ backgroundColor: '#DB7093' }}>

        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {uploadSuccess && <p className="text-green-500 mt-2">File processed successfully</p>}
      {uploadError && <p className="text-red-500 mt-2">Failed to upload file</p>}
    </div>
  );
};

export default FileUpload;