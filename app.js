//hello NAQ reviewer :D//



// Base URL for backend API
const API_BASE_URL = "http://localhost:5001";

let universities = [];
let currentScale = null;

// Page finishes loading
document.addEventListener('DOMContentLoaded', async () => {
    await loadUniversities();
    addCourseRow();
    setupEventListeners();
});


// Choose university options from backend 
async function loadUniversities() {
    console.log('Loading...');
    try {
        const response = await fetch(`${API_BASE_URL}/universities`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        universities = await response.json();
        console.log('Universities loaded:', universities.length);
        
        const universitySelect = document.getElementById('university');
        universities.forEach(uni => {
            const option = document.createElement('option');
            option.value = uni.key;
            option.textContent = `${uni.name} (${uni.scale})`;
            universitySelect.appendChild(option);
        });
        console.log('University options added to select');
    } catch (error) {
        console.error('Error loading universities:', error);
        showError('Failed to load universities. Make sure Flask server is running on http://localhost:5001');
    }
}


// UI event listeners
function setupEventListeners() {
    document.getElementById('university').addEventListener('change', handleUniversityChange);
    document.getElementById('add-course').addEventListener('click', addCourseRow);
    document.getElementById('gpa-form').addEventListener('submit', calculateGPA);
    document.getElementById('clear-all').addEventListener('click', clearAll);
}

// Update info/conversions
function handleUniversityChange(event) {
    const universityKey = event.target.value;
    const scaleInfo = document.getElementById('scale-info');
    
    if (universityKey) {
        const university = universities.find(u => u.key === universityKey);
        currentScale = university;
        
        scaleInfo.innerHTML = `<strong>Selected Scale:</strong> ${university.scale}`;
        scaleInfo.style.display = 'block';
        
        updateAllGradeConversions();
    } else {
        scaleInfo.style.display = 'none';
        currentScale = null;
    }
    
    clearResults();
}

// Adds a new course input row to  table
function addCourseRow() {
    const tbody = document.getElementById('courses');
    const row = document.createElement('tr');
    row.className = 'course-row';
    
    let yearOptions = '<option value="">Select Academic Year</option>';
    for (let year = 2010; year <= 2030; year++) {
        yearOptions += `<option value="${year}-${year+1}">Academic Year ${year}-${year+1}</option>`;
    }
    
    const placeholder = currentScale ? getGradePlaceholder(currentScale.scale) : 'Enter grade';
    
    row.innerHTML = `
        <td><input type="text" name="course" placeholder="Course Name" class="course-input"></td>
        <td><input type="text" name="grade" placeholder="${placeholder}" class="grade-input" required></td>
        <td><input type="number" name="credits" placeholder="3.0" step="0.1" min="0" class="credit-input" required></td>
        <td><select name="academic-year" class="year-select">${yearOptions}</select></td>
        <td class="gpa-display">-</td>
        <td class="alberta-gpa-display">-</td>
        <td class="manitoba-gpa-display">-</td>
        <td class="percentage-display">-</td>
        <td><button type="button" class="remove-btn" onclick="removeRow(this)">Remove</button></td>
    `;
        
  
  // Automatically convert grade 
    const gradeInput = row.querySelector('.grade-input');
    gradeInput.addEventListener('input', () => convertGradeRealTime(gradeInput));
    
    tbody.appendChild(row);
}

// Remove a specific course row
function removeRow(button) {
    button.closest('tr').remove();
}

function getGradePlaceholder(scaleName) {
    if (scaleName.includes('Percentage')) {
        return 'Enter percentage (0-100)';
    } else {
        return 'Enter letter grade (A+, A, B+, etc.)';
    }
}

// percentage -> LG using UBC's A+ scale
function convertPercentageToLetterGrade(percentage) {
    /**
     * Convert percentage to letter grade using UBC's official conversion tables
     * Uses Table 1 (with A+) by default - most universities have A+
     */
    if (percentage >= 95) return 'A+';
    if (percentage >= 87) return 'A';
    if (percentage >= 82) return 'A-';
    if (percentage >= 78) return 'B+';
    if (percentage >= 74) return 'B';
    if (percentage >= 70) return 'B-';
    if (percentage >= 66) return 'C+';
    if (percentage >= 62) return 'C';
    if (percentage >= 58) return 'C-';
    if (percentage >= 54) return 'D+';
    if (percentage >= 50) return 'D';
    if (percentage >= 46) return 'D-';
    return 'F';
}

// LG -> %
function convertGradeToPercentage(grade, university) {
    /**
     * Convert grade to percentage estimate
     * Now shows percentages even for percentage-based scales (for UBC adjusted averages)
     */
    if (!currentScale) return null;
    
    const gradeStr = String(grade).trim();
    
    // If current university uses percentage scale
    if (currentScale.scale.includes('Percentage')) {
        // If input is already a percentage, just return it
        const numericGrade = parseFloat(gradeStr);
        if (!isNaN(numericGrade) && numericGrade >= 0 && numericGrade <= 100) {
            return Math.round(numericGrade); // Return the percentage as-is
        }
        return null;
    }
    
    // For letter grade scales, convert to percentage using UBC tables
    const gradeUpper = gradeStr.toUpperCase();
    
    // Check if current scale has A+ to determine which UBC table to use
    const hasAPlus = currentScale.scale_key !== 'scale8'; // McGill/Quest don't have A+
    
    if (hasAPlus) {
        // Table 1 - For schools with A+ grades
        const letterToPercentage = {
            "A+": 95, "A": 87, "A-": 82, "B+": 78, "B": 74, "B-": 70,
            "C+": 66, "C": 62, "C-": 58, "D+": 54, "D": 50, "D-": 46, 
            "F": 25, "E": 25
        };
        return letterToPercentage[gradeUpper] || null;
    } else {
        // Table 2 - For schools without A+ grades
        const letterToPercentage = {
            "A": 95, "A-": 82, "B+": 78, "B": 74, "B-": 70,
            "C+": 66, "C": 62, "C-": 58, "D+": 54, "D": 50, "D-": 46,
            "F": 25, "E": 25
        };
        return letterToPercentage[gradeUpper] || null;
    }
}


// Convert grade input in real-time, update GPA & percentage displays
async function convertGradeRealTime(gradeInput) {
    if (!currentScale || !gradeInput.value.trim()) {
        const row = gradeInput.closest('tr');
        row.querySelector('.gpa-display').textContent = '-';
        row.querySelector('.alberta-gpa-display').textContent = '-';
        row.querySelector('.manitoba-gpa-display').textContent = '-';
        row.querySelector('.percentage-display').textContent = '-';
        return;
    }
    
    try {
        // Get primary GPA conversion
        const response = await fetch(`${API_BASE_URL}/convert-grade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                grade: gradeInput.value.trim(),
                university: currentScale.key
            })
        });
        
        const result = await response.json();
        const row = gradeInput.closest('tr');
        const gpaDisplay = row.querySelector('.gpa-display');
        const albertaDisplay = row.querySelector('.alberta-gpa-display');
        const manitobaDisplay = row.querySelector('.manitoba-gpa-display');
        const percentageDisplay = row.querySelector('.percentage-display');
        
        // Primary GPA
        if (result.gpa !== null && result.gpa !== undefined) {
            gpaDisplay.textContent = result.gpa.toFixed(2);
            gpaDisplay.style.color = '#2c5530';
        } else {
            gpaDisplay.textContent = 'Invalid';
            gpaDisplay.style.color = '#a94442';
        }

        // Get Alberta conversion
        const albertaResponse = await fetch(`${API_BASE_URL}/convert-grade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                grade: gradeInput.value.trim(),
                university: 'alberta'
            })
        });
        const albertaResult = await albertaResponse.json();

        // Get Manitoba conversion
        const manitobaResponse = await fetch(`${API_BASE_URL}/convert-grade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                grade: gradeInput.value.trim(),
                university: 'manitoba'
            })
        });
        const manitobaResult = await manitobaResponse.json();

        // Alberta GPA
        if (albertaResult.gpa !== null && albertaResult.gpa !== undefined) {
            albertaDisplay.textContent = albertaResult.gpa.toFixed(2);
            albertaDisplay.style.color = '#2c5530';
        } else {
            albertaDisplay.textContent = 'N/A';
            albertaDisplay.style.color = '#a94442';
        }

        // Manitoba GPA
        if (manitobaResult.gpa !== null && manitobaResult.gpa !== undefined) {
            manitobaDisplay.textContent = manitobaResult.gpa.toFixed(2);
            manitobaDisplay.style.color = '#2c5530';
        } else {
            manitobaDisplay.textContent = 'N/A';
            manitobaDisplay.style.color = '#a94442';
        }
        
        // Percentage conversion
        const percentageValue = convertGradeToPercentage(gradeInput.value.trim(), currentScale.key);
        if (percentageValue !== null) {
            percentageDisplay.textContent = percentageValue + '%';
            percentageDisplay.style.color = '#2c5530';
        } else {
            percentageDisplay.textContent = 'N/A';
            percentageDisplay.style.color = '#666';
        }
        
    } catch (error) {
        const row = gradeInput.closest('tr');
        row.querySelector('.gpa-display').textContent = 'Error';
        row.querySelector('.alberta-gpa-display').textContent = 'Error';
        row.querySelector('.manitoba-gpa-display').textContent = 'Error';
        row.querySelector('.percentage-display').textContent = 'Error';
    }
}

function updateAllGradeConversions() {
    const gradeInputs = document.querySelectorAll('.grade-input');
    gradeInputs.forEach(input => {
        if (input.value.trim()) {
            convertGradeRealTime(input);
        }
        input.placeholder = getGradePlaceholder(currentScale.scale);
    });
}

async function calculateGPA(event) {
    event.preventDefault();
    
    if (!currentScale) {
        showError('Please select a university first.');
        return;
    }
    
    const courseRows = document.querySelectorAll('.course-row');
    if (courseRows.length === 0) {
        showError('Please add at least one course.');
        return;
    }
    
    const courses = Array.from(courseRows).map(row => {
        const course = row.querySelector('[name="course"]').value || 'Course';
        const grade = row.querySelector('[name="grade"]').value.trim();
        const credits = parseFloat(row.querySelector('[name="credits"]').value) || 0;
        const academicYear = row.querySelector('[name="academic-year"]').value;
        
        return { course, grade, credits, academic_year: academicYear };
    });
    
    const validCourses = courses.filter(c => c.grade && c.credits > 0);
    if (validCourses.length === 0) {
        showError('Please enter valid grades and credits for at least one course.');
        return;
    }
    
    showLoading(true);
    clearError();
    
    try {
        const response = await fetch(`${API_BASE_URL}/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                university: currentScale.key,
                courses: validCourses
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Calculation failed');
        }
        
        const results = await response.json();
        displayResults(results);
        
    } catch (error) {
        showError(`Calculation failed: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function convertGpaToPercentage(gpa, scaleName) {
    /**
     * Convert GPA back to percentage for display purposes
     * Only works for percentage-based scales like UBC
     */
    if (!scaleName.includes('Percentage')) {
        return null; // Only convert for percentage scales
    }
    
    // Based on Scale 3 (Percentage) conversions
    if (gpa >= 4.00) return 92; // 90-100% range, use middle-high
    if (gpa >= 3.90) return 87; // 85-89% range, use middle
    if (gpa >= 3.70) return 82; // 80-84% range, use middle
    if (gpa >= 3.30) return 78; // 77-79% range, use middle
    if (gpa >= 3.00) return 75; // 73-76% range, use middle
    if (gpa >= 2.70) return 71; // 70-72% range, use middle
    if (gpa >= 2.30) return 68; // 67-69% range, use middle
    if (gpa >= 2.00) return 65; // 63-66% range, use middle
    if (gpa >= 1.70) return 61; // 60-62% range, use middle
    if (gpa >= 1.30) return 58; // 57-59% range, use middle
    if (gpa >= 1.00) return 55; // 53-56% range, use middle
    if (gpa >= 0.70) return 51; // 50-52% range, use middle
    return 45; // Below 50%
}

function displayResults(results) {
    const resultsSection = document.getElementById('results-section');
    const resultsDiv = document.getElementById('results');
    
    let html = `
        <div class="result-header">
            <h3>University: ${results.university.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
            <p>Primary Scale: ${results.primary_scale}</p>
        </div>
    `;
    
    const primaryResults = results.primary_results;
    
    // Primary Scale Cumulative GPA
    html += `
        <div class="gpa-result primary">
            <h4>Cumulative GPA (cGPA) - ${results.primary_scale}</h4>
            <div class="gpa-value">${primaryResults.cGPA}</div>
            <p class="gpa-details">Based on ${primaryResults.total_courses} courses (${primaryResults.total_credits} total credits)</p>
        </div>
    `;
    
    // Year breakdown
    if (primaryResults.year_breakdown && primaryResults.year_breakdown.length > 0) {
        html += '<div class="gpa-result"><h4>Year-by-Year Breakdown</h4><ul>';
        primaryResults.year_breakdown
            .sort((a, b) => b.year.localeCompare(a.year))
            .forEach(year => {
                html += `<li><strong>${year.year}:</strong> ${year.gpa} GPA (${year.credits} credits, ${year.courses} courses)</li>`;
            });
        html += '</ul></div>';
    }
    
    // Adjusted GPA (Drop worst year)
    if (primaryResults.adjusted_gpa !== undefined) {
        html += `
            <div class="gpa-result weighted">
                <h4>Adjusted GPA (Worst Year Dropped)</h4>
                <div class="gpa-value">${primaryResults.adjusted_gpa}</div>
                <p class="gpa-details">
                    Dropped: ${primaryResults.dropped_year}
                    ${primaryResults.adjusted_note ? `<br><em>${primaryResults.adjusted_note}</em>` : ''}
                    <br><strong>Used by:</strong> University of Calgary, University of Alberta, UBC
                </p>
            </div>
        `;
    }
    
    // Two Best Years GPA (Western)
    if (primaryResults.two_best_years_gpa !== undefined) {
        html += `
            <div class="gpa-result weighted">
                <h4>Two Best Years GPA</h4>
                <div class="gpa-value">${primaryResults.two_best_years_gpa}</div>
                <p class="gpa-details">
                    Years used: ${primaryResults.best_two_years.join(', ')}
                    <br><strong>Used by:</strong> Western University
                </p>
            </div>
        `;
    }
    
    // Two Most Recent Years GPA (Dalhousie)
    if (primaryResults.two_recent_years_gpa !== undefined) {
        html += `
            <div class="gpa-result weighted">
                <h4>Two Most Recent Years GPA</h4>
                <div class="gpa-value">${primaryResults.two_recent_years_gpa}</div>
                <p class="gpa-details">
                    Years used: ${primaryResults.recent_two_years.join(', ')}
                    <br><strong>Used by:</strong> Dalhousie University
                </p>
            </div>
        `;
    }
    
    // Three Most Recent Years GPA
    if (primaryResults.three_recent_years_gpa !== undefined) {
        html += `
            <div class="gpa-result weighted">
                <h4>Three Most Recent Years GPA</h4>
                <div class="gpa-value">${primaryResults.three_recent_years_gpa}</div>
                <p class="gpa-details">
                    Years used: ${primaryResults.recent_three_years.join(', ')}
                    <br><strong>Used by:</strong> University of Ottawa
                </p>
            </div>
        `;
    }
    
    // Important notes
    html += `
        <div class="gpa-result info">
            <h4>Important Notes</h4>
            <ul>
                <li><strong>Table Columns:</strong> Shows conversions to different GPA scales and percentage estimates side-by-side</li>
                <li><strong>Alberta/Calgary Scale:</strong> A+ and A both equal 4.0</li>
                <li><strong>Manitoba Scale:</strong> Uses 4.5 scale where A+ = 4.5</li>
                <li><strong>Percentage Est.:</strong> Approximate percentage equivalents for letter grades (shows N/A if already percentage scale)</li>
                <li>Different medical schools use different calculation methods</li>
                <li>Some schools require minimum 18 credits per year for "worst year" dropping</li>
                <li>Always verify GPA calculations with official school requirements</li>
            </ul>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => errorDiv.style.display = 'none', 8000);
}

function clearError() {
    document.getElementById('error').style.display = 'none';
}

function clearResults() {
    document.getElementById('results-section').style.display = 'none';
}

function clearAll() {
    document.getElementById('courses').innerHTML = '';
    document.getElementById('university').value = '';
    document.getElementById('scale-info').style.display = 'none';
    currentScale = null;
    clearResults();
    clearError();
    addCourseRow();
}
