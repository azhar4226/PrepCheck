// Browser Console Test Script for SubjectManagement and Notifications
// Copy and paste this into the browser console on the PrepCheck app

console.log('=== PrepCheck Frontend Test ===');

// Test if Vue app is loaded
if (window.Vue || document.querySelector('#app').__vue__) {
    console.log('✅ Vue app detected');
} else {
    console.log('❌ Vue app not found');
}

// Test API service availability 
if (window.apiService) {
    console.log('✅ API service available globally');
} else {
    console.log('⚠️ API service not available globally - will test axios directly');
}

// Test localStorage for auth
const token = localStorage.getItem('prepcheck_token');
const user = localStorage.getItem('prepcheck_user');

console.log('Auth Status:');
console.log('- Token:', token ? '✅ Present' : '❌ Missing');
console.log('- User:', user ? '✅ Present' : '❌ Missing');

if (token) {
    // Test API calls
    console.log('\n=== Testing API Calls ===');
    
    // Test subjects endpoint
    fetch('/api/admin/subjects', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Subjects API response:', data);
    })
    .catch(error => {
        console.log('❌ Subjects API error:', error);
    });
    
    // Test notifications endpoint
    fetch('/api/notifications?limit=10', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Notifications API response:', data);
    })
    .catch(error => {
        console.log('❌ Notifications API error:', error);
    });
    
    // Test creating a subject
    fetch('/api/admin/subjects', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: 'Browser Test Subject',
            description: 'Created from browser console test',
            is_active: true
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Create Subject API response:', data);
        
        // Test deleting the created subject
        if (data.subject && data.subject.id) {
            fetch(`/api/admin/subjects/${data.subject.id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(deleteData => {
                console.log('✅ Delete Subject API response:', deleteData);
            })
            .catch(error => {
                console.log('❌ Delete Subject API error:', error);
            });
        }
    })
    .catch(error => {
        console.log('❌ Create Subject API error:', error);
    });
    
} else {
    console.log('\n⚠️ Please login first to test authenticated endpoints');
}

// Check current route
console.log('\nCurrent location:', window.location.pathname);

// Check for any JavaScript errors
console.log('\n=== Checking for Errors ===');
window.addEventListener('error', function(e) {
    console.log('❌ JavaScript Error:', e.error);
});

console.log('Test script loaded. Check the network tab for API calls.');
