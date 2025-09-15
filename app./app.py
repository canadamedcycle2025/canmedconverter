# a lot less time than front end tbh
# to do: manitoba stuff, change maybe for US schools?


from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#bug testing
@app.route("/test")
def test_route():
    return jsonify({"message": "Flask server is working!", "status": "ok"})

#  Conversion Scales with new Alberta and Manitoba scales
CONVERSION_SCALES = {
    "scale3": {
        "name": "Scale 3 (Percentage)",
        "conversions": {
            (90, 100): 4.00, (85, 89): 3.90, (80, 84): 3.70, (77, 79): 3.30,
            (73, 76): 3.00, (70, 72): 2.70, (67, 69): 2.30, (63, 66): 2.00,
            (60, 62): 1.70, (57, 59): 1.30, (53, 56): 1.00, (50, 52): 0.70,
            (0, 49): 0.00
        },
        "type": "percentage"
    },
    "scale6": {
        "name": "Scale 6 (Memorial University)",
        "conversions": {
            (94, 100): 4.00, (87, 93): 3.90, (80, 86): 3.70, (75, 79): 3.30,
            (70, 74): 3.00, (65, 69): 2.70, (60, 64): 2.30, (55, 59): 2.00,
            (50, 54): 1.70, (0, 49): 0.00
        },
        "type": "percentage"
    },
    "scale7": {
        "name": "Scale 7 (Letter Grades)",
        "conversions": {
            "A+": 4.00, "A": 3.90, "A-": 3.70, "B+": 3.30, "B": 3.00,
            "B-": 2.70, "C+": 2.30, "C": 2.00, "C-": 1.70, "D+": 1.30,
            "D": 1.00, "D-": 0.70, "F": 0.00, "E": 0.00
        },
        "type": "letter"
    },
    "scale8": {
        "name": "Scale 8 (McGill/Quest)",
        "conversions": {
            "A": 4.00, "A-": 3.70, "B+": 3.30, "B": 3.00, "B-": 2.70,
            "C+": 2.30, "C": 2.00, "C-": 1.70, "D+": 1.30, "D": 1.00,
            "F": 0.00
        },
        "type": "letter"
    },
    "scale9": {
        "name": "Scale 9 (York University)",
        "conversions": {
            "A+": 4.00, "A": 3.90, "B+": 3.30, "B": 3.00, "C+": 2.30,
            "C": 2.00, "D+": 1.30, "D": 1.00, "F": 0.00
        },
        "type": "letter"
    },
    "alberta_4_0": {
        "name": "Alberta/Calgary 4.0 Scale",
        "conversions": {
            "A+": 4.00, "A": 4.00, "A-": 3.70, "B+": 3.30, "B": 3.00,
            "B-": 2.70, "C+": 2.30, "C": 2.00, "C-": 1.70, "D+": 1.30,
            "D": 1.00, "D-": 0.70, "F": 0.00
        },
        "type": "letter"
    },
    "manitoba_4_5": {
        "name": "Manitoba 4.5 Scale",
        "conversions": {
            "A+": 4.50, "A": 4.00, "A-": 4.00, "B+": 3.50, "B": 3.00,
            "B-": 3.00, "C+": 2.50, "C": 2.00, "C-": 2.00, "D+": 1.00,
            "D": 1.00, "D-": 1.00, "F": 0.00
        },
        "type": "letter"
    }
}

# University to scale mapping
UNIVERSITY_SCALES = {
    "algoma": "scale3", "bishops": "scale3", "brock": "scale3", "cape_breton": "scale3",
    "guelph": "scale3", "lakehead": "scale3", "nipissing": "scale3", "ocad": "scale3",
    "pei": "scale3", "regina": "scale3", "saskatchewan": "scale3", "st_fx": "scale3",
    "trent": "scale3", "western": "scale3",
    
    "acadia": "scale7", "athabasca": "scale7", "brandon": "scale7",
    "carleton": "scale7", "capilano": "scale7", "concordia": "scale7",
    "laurentian": "scale7", "laval": "scale7", "lethbridge": "scale7", "mcmaster": "scale7",
    "moncton": "scale7", "montreal": "scale7", "mount_allison": "scale7", "mount_royal": "scale7",
    "mount_saint_vincent": "scale7", "unb": "scale7", "ontario_tech": "scale7", "ottawa": "scale7",
    "uqam": "scale7", "royal_roads": "scale7", "sherbrooke": "scale7", "sfu": "scale7",
    "saint_marys": "scale7", "st_thomas": "scale7", "sainte_anne": "scale7", "tru": "scale7",
    "tmu": "scale7", "trinity_western": "scale7", "ubc": "scale7", "unbc": "scale7",
    "laurier": "scale7", "winnipeg": "scale7",
    
    # Alberta schools use their own 4.0 scale where A+ and A are both 4.0
    "alberta": "alberta_4_0",
    "calgary": "alberta_4_0",
    
    "memorial": "scale6",
    "mcgill": "scale8", "quest": "scale8",
    
    # Manitoba uses their own 4.5 scale
    "manitoba": "manitoba_4_5",
    "york": "scale9"
}

def convert_percentage_to_letter_grade(percentage):
    """Convert percentage to letter grade using standard mapping."""
    try:
        numeric_grade = float(percentage)
        if numeric_grade >= 90: return 'A+'
        if numeric_grade >= 85: return 'A'
        if numeric_grade >= 80: return 'A-'
        if numeric_grade >= 77: return 'B+'
        if numeric_grade >= 73: return 'B'
        if numeric_grade >= 70: return 'B-'
        if numeric_grade >= 67: return 'C+'
        if numeric_grade >= 63: return 'C'
        if numeric_grade >= 60: return 'C-'
        if numeric_grade >= 57: return 'D+'
        if numeric_grade >= 53: return 'D'
        if numeric_grade >= 50: return 'D-'
        return 'F'
    except (ValueError, TypeError):
        return None

def convert_grade_to_gpa(grade, scale_type):
    """Convert a grade to GPA using the specified scale."""
    if not scale_type or scale_type not in CONVERSION_SCALES:
        return None
    
    scale = CONVERSION_SCALES[scale_type]
    grade_str = str(grade).strip().upper()
    
    if scale["type"] == "percentage":
        try:
            numeric_grade = float(grade_str)
            if numeric_grade < 0 or numeric_grade > 100:
                return None
                
            for (min_val, max_val), gpa_val in scale["conversions"].items():
                if min_val <= numeric_grade <= max_val:
                    return gpa_val
        except ValueError:
            return None
    else:  # letter grades
        # If we get a number but need a letter grade, convert it
        try:
            numeric_grade = float(grade_str)
            if 0 <= numeric_grade <= 100:
                letter_grade = convert_percentage_to_letter_grade(numeric_grade)
                return scale["conversions"].get(letter_grade)
        except ValueError:
            # Not a number, treat as letter grade
            pass
        
        return scale["conversions"].get(grade_str)
    
    return None

def convert_grade_to_percentage(grade, scale_type):
    """Convert letter grade to percentage estimate. Returns None if already percentage scale."""
    if not scale_type or scale_type not in CONVERSION_SCALES:
        return None
    
    scale = CONVERSION_SCALES[scale_type]
    
    # If the scale is already percentage-based, return None
    if scale["type"] == "percentage":
        return None
    
    # Check if this scale has A+
    has_a_plus = "A+" in scale["conversions"]
    
    # Convert letter grade to percentage estimate using UBC tables
    return convert_letter_to_percentage_ubc(grade, has_a_plus)

def calculate_gpa_variations(courses_with_years):
    """Calculate various GPA types used by different medical schools."""
    results = {}
    
    year_data = {}
    all_courses = []
    
    for course in courses_with_years:
        gpa = course["gpa"]
        credits = course["credits"]
        year = course.get("academic_year")
        
        if gpa is not None and credits > 0:
            course_data = {"gpa": gpa, "credits": credits, "year": year, "course": course["course"]}
            all_courses.append(course_data)
            
            if year:
                if year not in year_data:
                    year_data[year] = {"courses": [], "total_credits": 0, "weighted_sum": 0}
                year_data[year]["courses"].append(course_data)
                year_data[year]["total_credits"] += credits
                year_data[year]["weighted_sum"] += gpa * credits
    
    if not all_courses:
        return {"error": "No valid courses found"}
    
    # Cumulative GPA
    total_credits = sum(course["credits"] for course in all_courses)
    total_weighted_sum = sum(course["gpa"] * course["credits"] for course in all_courses)
    results["cGPA"] = round(total_weighted_sum / total_credits, 3) if total_credits > 0 else 0
    results["total_courses"] = len(all_courses)
    results["total_credits"] = round(total_credits, 1)
    
    # Year averages
    year_averages = []
    for year, data in year_data.items():
        if data["total_credits"] > 0:
            year_averages.append({
                "year": year,
                "gpa": round(data["weighted_sum"] / data["total_credits"], 3),
                "credits": round(data["total_credits"], 1),
                "courses": len(data["courses"])
            })
    
    year_averages.sort(key=lambda x: x["gpa"])
    results["year_breakdown"] = year_averages
    
    # UBC Adjusted GPA (Drop 30 lowest credit hours)
    if total_credits >= 30:
        # Sort all courses by GPA (lowest first)
        sorted_courses = sorted(all_courses, key=lambda x: x["gpa"])
        
        # Remove lowest courses until we've dropped 30 credits
        remaining_courses = all_courses.copy()
        dropped_credits = 0
        dropped_courses = []
        
        for course in sorted_courses:
            if dropped_credits + course["credits"] <= 30:
                remaining_courses.remove(course)
                dropped_courses.append(course)
                dropped_credits += course["credits"]
            elif dropped_credits < 30:
                # Need to partially drop this course
                partial_drop = 30 - dropped_credits
                course_copy = course.copy()
                course_copy["credits"] = partial_drop
                dropped_courses.append(course_copy)
                
                # Update the remaining course with reduced credits
                for remaining in remaining_courses:
                    if remaining is course:
                        remaining["credits"] -= partial_drop
                        break
                dropped_credits = 30
                break
        
        if remaining_courses:
            ubc_total_credits = sum(course["credits"] for course in remaining_courses)
            ubc_weighted_sum = sum(course["gpa"] * course["credits"] for course in remaining_courses)
            
            results["ubc_adjusted_gpa"] = round(ubc_weighted_sum / ubc_total_credits, 3) if ubc_total_credits > 0 else 0
            results["ubc_dropped_credits"] = round(dropped_credits, 1)
            results["ubc_dropped_courses"] = [f"{c['course']} ({c['credits']} credits)" for c in dropped_courses]
    
    # Adjusted GPA (Drop worst year) - Calgary, Alberta
    if len(year_averages) >= 2:
        full_years = [year for year in year_averages if year["credits"] >= 18]
        
        if len(full_years) >= 2:
            remaining_years = full_years[1:]
            adjusted_credits = sum(year["credits"] for year in remaining_years)
            adjusted_weighted_sum = sum(year["gpa"] * year["credits"] for year in remaining_years)
            
            results["adjusted_gpa"] = round(adjusted_weighted_sum / adjusted_credits, 3) if adjusted_credits > 0 else 0
            results["dropped_year"] = full_years[0]["year"]
        elif len(year_averages) >= 2:
            remaining_years = year_averages[1:]
            adjusted_credits = sum(year["credits"] for year in remaining_years)
            adjusted_weighted_sum = sum(year["gpa"] * year["credits"] for year in remaining_years)
            
            results["adjusted_gpa"] = round(adjusted_weighted_sum / adjusted_credits, 3) if adjusted_credits > 0 else 0
            results["dropped_year"] = year_averages[0]["year"]
            results["adjusted_note"] = "Note: Dropped year had fewer than 18 credits"
    
    # Two Best Years GPA (Western University)
    if len(year_averages) >= 2:
        best_two_years = sorted(year_averages, key=lambda x: x["gpa"], reverse=True)[:2]
        best_two_credits = sum(year["credits"] for year in best_two_years)
        best_two_weighted_sum = sum(year["gpa"] * year["credits"] for year in best_two_years)
        
        results["two_best_years_gpa"] = round(best_two_weighted_sum / best_two_credits, 3) if best_two_credits > 0 else 0
        results["best_two_years"] = [year["year"] for year in best_two_years]
    
    # Two Most Recent Years GPA (Dalhousie University)
    if len(year_averages) >= 2:
        recent_two = sorted(year_averages, key=lambda x: x["year"], reverse=True)[:2]
        recent_two_credits = sum(year["credits"] for year in recent_two)
        recent_two_weighted_sum = sum(year["gpa"] * year["credits"] for year in recent_two)
        
        results["two_recent_years_gpa"] = round(recent_two_weighted_sum / recent_two_credits, 3) if recent_two_credits > 0 else 0
        results["recent_two_years"] = [year["year"] for year in recent_two]
    
    # Three Most Recent Years GPA (University of Ottawa)
    if len(year_averages) >= 3:
        recent_three = sorted(year_averages, key=lambda x: x["year"], reverse=True)[:3]
        recent_three_credits = sum(year["credits"] for year in recent_three)
        recent_three_weighted_sum = sum(year["gpa"] * year["credits"] for year in recent_three)
        
        results["three_recent_years_gpa"] = round(recent_three_weighted_sum / recent_three_credits, 3) if recent_three_credits > 0 else 0
        results["recent_three_years"] = [year["year"] for year in recent_three]
    
    return results

@app.route("/universities", methods=["GET"])
def get_universities():
    """Return list of supported universities with their scales."""
    universities = []
    for uni_key, scale_key in UNIVERSITY_SCALES.items():
        scale_info = CONVERSION_SCALES[scale_key]
        universities.append({
            "key": uni_key,
            "name": uni_key.replace("_", " ").title(),
            "scale": scale_info["name"],
            "scale_key": scale_key
        })
    return jsonify(universities)

@app.route("/calculate", methods=["POST"])
def calculate_gpa():
    """Calculate GPA with multiple scale comparisons."""
    try:
        data = request.get_json()
        university = data.get("university", "").lower()
        courses = data.get("courses", [])
        
        if university not in UNIVERSITY_SCALES:
            return jsonify({"error": "University not supported"}), 400
        
        primary_scale = UNIVERSITY_SCALES[university]
        processed_courses = []
        
        for course in courses:
            primary_gpa = convert_grade_to_gpa(course["grade"], primary_scale)
            alberta_gpa = convert_grade_to_gpa(course["grade"], "alberta_4_0")
            manitoba_gpa = convert_grade_to_gpa(course["grade"], "manitoba_4_5")
            percentage_conversion = convert_grade_to_percentage(course["grade"], primary_scale)
            
            processed_courses.append({
                "course": course.get("course", "Course"),
                "original_grade": course["grade"],
                "credits": float(course.get("credits", 1)),
                "academic_year": course.get("academic_year"),
                "gpa": primary_gpa,
                "alberta_gpa": alberta_gpa,
                "manitoba_gpa": manitoba_gpa,
                "percentage": percentage_conversion
            })
        
        # Calculate primary scale results
        primary_results = calculate_gpa_variations(processed_courses)
        
        if "error" in primary_results:
            return jsonify(primary_results), 400
        
        # Calculate comparative scales
        comparative_results = {}
        
        # Alberta 4.0 Scale
        if primary_scale != "alberta_4_0":
            alberta_courses = []
            for course in processed_courses:
                if course["alberta_gpa"] is not None:
                    alberta_course = course.copy()
                    alberta_course["gpa"] = course["alberta_gpa"]
                    alberta_courses.append(alberta_course)
            if alberta_courses:
                alberta_calc = calculate_gpa_variations(alberta_courses)
                comparative_results["alberta_4_0"] = {
                    "scale_name": "Alberta/Calgary 4.0 Scale",
                    "cGPA": alberta_calc.get("cGPA"),
                    "adjusted_gpa": alberta_calc.get("adjusted_gpa")
                }
        
        # Manitoba 4.5 Scale
        if primary_scale != "manitoba_4_5":
            manitoba_courses = []
            for course in processed_courses:
                if course["manitoba_gpa"] is not None:
                    manitoba_course = course.copy()
                    manitoba_course["gpa"] = course["manitoba_gpa"]
                    manitoba_courses.append(manitoba_course)
            if manitoba_courses:
                manitoba_calc = calculate_gpa_variations(manitoba_courses)
                comparative_results["manitoba_4_5"] = {
                    "scale_name": "Manitoba 4.5 Scale",
                    "cGPA": manitoba_calc.get("cGPA"),
                    "adjusted_gpa": manitoba_calc.get("adjusted_gpa")
                }
        
        response = {
            "university": university,
            "primary_scale": CONVERSION_SCALES[primary_scale]["name"],
            "courses": processed_courses,
            "primary_results": primary_results,
            "comparative_scales": comparative_results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/convert-grade", methods=["POST"])
def convert_single_grade():
    """Convert a single grade for real-time feedback."""
    try:
        data = request.get_json()
        grade = data.get("grade")
        university = data.get("university", "").lower()
        
        if university not in UNIVERSITY_SCALES:
            return jsonify({"error": "University not supported"}), 400
        
        scale_type = UNIVERSITY_SCALES[university]
        gpa = convert_grade_to_gpa(grade, scale_type)
        
        return jsonify({
            "original_grade": grade,
            "gpa": gpa,
            "scale": CONVERSION_SCALES[scale_type]["name"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def is_percentage_scale(scale_type):
    """Check if the scale type is percentage-based."""
    return CONVERSION_SCALES.get(scale_type, {}).get("type") == "percentage"

def convert_letter_to_percentage(grade):
    """Convert letter grade to percentage estimate."""
    grade_str = str(grade).strip().upper()
    
    # Basic letter grade to percentage mapping
    letter_to_percentage = {
        "A+": 95, "A": 87, "A-": 82,
        "B+": 78, "B": 75, "B-": 72,
        "C+": 68, "C": 65, "C-": 62,
        "D+": 58, "D": 55, "D-": 52,
        "F": 25, "E": 25
    }
    
    return letter_to_percentage.get(grade_str)

@app.route("/convert-to-percentage", methods=["POST"])
def convert_to_percentage():
    """Convert letter grade to percentage, return null if already percentage scale."""
    try:
        data = request.get_json()
        grade = data.get("grade")
        university = data.get("university", "").lower()
        
        if university not in UNIVERSITY_SCALES:
            return jsonify({"error": "University not supported"}), 400
        
        scale_type = UNIVERSITY_SCALES[university]
        
        # If the user's university already uses percentage scale, return null
        if is_percentage_scale(scale_type):
            return jsonify({
                "original_grade": grade,
                "percentage": None,
                "note": "Already percentage scale"
            })
        
        # Convert letter grade to percentage
        percentage = convert_letter_to_percentage(grade)
        
        return jsonify({
            "original_grade": grade,
            "percentage": percentage
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
