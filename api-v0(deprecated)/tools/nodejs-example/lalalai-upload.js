const axios = require('axios');
const fs = require('fs');

const fileName = '~/file.mp3';

try {
    const data = fs.readFileSync(fileName);
    try {
        (axios.post('https://www.lalal.ai/api/upload/', data, {
            headers: {
                'Content-Disposition': 'attachment; filename=file.mp3',
                'Authorization': 'license <PASTE LICENSE HERE>'
            }
        })).then(res => console.log('Result:', res.data))
    }
    catch (error) {
        console.error('Error:', error);
    }
} catch (error) {
    console.error('Error:', error);
}

