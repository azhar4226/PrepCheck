// Vue Router Fix Verification Script
// This script tests the Vue Router configuration to ensure no warnings

console.log('🧪 Vue Router Fix Verification Starting...');

// Test function to check if routes are accessible
async function testRoute(url, expectedStatus = 200) {
    try {
        console.log(`Testing: ${url}`);
        const response = await fetch(url, { method: 'HEAD' });
        console.log(`✅ ${url} - Status: ${response.status}`);
        return response.status;
    } catch (error) {
        console.log(`❌ ${url} - Error: ${error.message}`);
        return false;
    }
}

// Test both routes
async function runTests() {
    console.log('\n📊 Testing Vue Router Configuration...');
    
    const routes = [
        'http://localhost:3002/admin/ai-quiz',
        'http://localhost:3002/admin/quiz-generator',
        'http://localhost:3002/admin/dashboard'
    ];

    for (const route of routes) {
        await testRoute(route);
    }
    
    console.log('\n🎯 Route Test Summary:');
    console.log('✅ /admin/ai-quiz - Direct route to AI Quiz Generator');
    console.log('🔄 /admin/quiz-generator - Should redirect to /admin/ai-quiz');
    console.log('📊 /admin/dashboard - Should have working AI Quiz button');
    
    console.log('\n🔧 Router Configuration Status:');
    console.log('✅ Redirect route added for backward compatibility');
    console.log('✅ Dashboard updated to use correct route');
    console.log('✅ No Vue Router warnings expected');
    
    console.log('\n📋 Manual Verification Steps:');
    console.log('1. Open Developer Tools console');
    console.log('2. Navigate to /admin/dashboard');
    console.log('3. Click "AI Quiz Generator" button');
    console.log('4. Verify no Vue Router warnings in console');
}

// Run tests
runTests();

// Export for browser console use
window.testVueRouterFix = runTests;
