from flask import Flask, request, render_template_string
import random

app = Flask(__name__)

# Preload 1000 health facts (sample for brevity)
HEALTH_FACTS = [
    "Drinking water can help control calories.",
    "Exercise boosts brain function.",
    "Protein is essential for muscle repair.",
    "Regular physical activity reduces risk of chronic diseases.",
    "Adequate sleep improves weight loss results.",
    # Add up to 1000 facts here or generate dynamically
]
HEALTH_FACTS *= 200

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Weight a Minute - Fitness Calorie Calculator</title>
    <style>
        body {
            background-color: #1e3a8a;
            background-image: url('data:image/svg;utf8,<svg fill="white" fill-opacity="0.05" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24"><path d="M21 7h-2V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v2H3v10h2v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2h2V7zm-4-2v2H7V5zm-7 14v-2h7v2z"/></svg>');
            background-repeat: repeat;
            background-position: center;
            background-size: 60px 60px;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
        }
        header { width: 100%; text-align: center; margin-bottom: 30px; }
        header h1 { font-size: 2.5rem; font-weight: 700; letter-spacing: 2px; }
        form { flex: 1 1 450px; min-width: 320px; }
        label { font-weight: 600; display: block; margin-top: 15px; }
        input[type=range], input[type=number], select, button {
            width: 100%; padding: 10px; margin-top: 6px; border-radius: 6px; border: none; box-sizing: border-box; font-size: 1rem;
        }
        input[type=range] { background: transparent; }
        select, input[type=number] { background: #3b82f6; color: white; }
        button { background-color: #2563eb; color: white; font-weight: 700; cursor: pointer; margin-top: 25px; transition: background-color 0.3s ease; }
        button:hover { background-color: #1d4ed8; }
        a { color: #93c5fd; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .slider-value { text-align: right; font-weight: 400; margin-top: 3px; color: #cbd5e1; }
        .info-text { font-size: 0.9rem; color: #a5b4fc; margin-top: 10px; }
        .side-info { flex: 1 1 350px; min-width: 300px; background: rgba(59, 130, 246, 0.15); border-radius: 12px; padding: 20px; color: #dbeafe; display: flex; flex-direction: column; justify-content: space-between; height: fit-content; }
        .fitness-importance { font-size: 1rem; line-height: 1.4; margin-bottom: 20px; }
        .health-fact { background: #2563eb; padding: 15px; border-radius: 10px; font-weight: 600; font-size: 1.1rem; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.25); }
    </style>
</head>
<body>
    <header>
        <h1>Weight a Minute</h1>
    </header>
    <form method="POST" action="/">
        <label for="age">Age:</label>
        <input type="number" id="age" name="age" min="10" max="100" required />

        <label for="weight">Weight (kg):</label>
        <input type="range" id="weight" name="weight" min="30" max="150" step="0.1" value="70" oninput="weightValue.innerText = this.value" />
        <div class="slider-value">Current: <span id="weightValue">70</span> kg</div>

        <label for="height">Height (cm):</label>
        <input type="range" id="height" name="height" min="100" max="220" value="170" oninput="heightValue.innerText = this.value" />
        <div class="slider-value">Current: <span id="heightValue">170</span> cm</div>

        <label for="gender">Gender:</label>
        <select id="gender" name="gender" required>
            <option value="male" selected>Male</option>
            <option value="female">Female</option>
        </select>

        <label for="activity_level">Activity Level:</label>
        <select id="activity_level" name="activity_level" required>
            <option value="1.2">Sedentary (little/no exercise)</option>
            <option value="1.375">Lightly active (1-3 days/week)</option>
            <option value="1.55">Moderately active (3-5 days/week)</option>
            <option value="1.725">Very active (6-7 days/week)</option>
            <option value="1.9">Extra active (hard physical job)</option>
        </select>

        <label for="weight_loss_goal">Target Weight Loss (kg):</label>
        <input type="number" id="weight_loss_goal" name="weight_loss_goal" min="0.1" step="0.1" value="0.5" required />
        <div class="info-text">Enter how many kilograms you want to lose to personalize your plan.</div>
        <label for="weeks_goal">Number of Weeks:</label>
        <input type="number" id="weeks_goal" name="weeks_goal" min="1" max="52" step="1" value="4" required />
        <div class="info-text">Enter the number of weeks to achieve your target weight loss.</div>

        <button type="submit">Calculate</button>
    </form>
    <div class="side-info">
        <div class="fitness-importance">
            <h2>Why Keep Fit?</h2>
            <p>Maintaining a healthy weight and regular exercise improves your overall health, reduces risk of chronic diseases, and enhances mental well-being. Balanced nutrition and fitness promote longevity and a better quality of life.</p>
        </div>
        <div class="health-fact">
            <h3>Health Fact of the Day</h3>
            <p>{{ health_fact }}</p>
        </div>
    </div>

<script>
    const weightSlider = document.getElementById('weight');
    const weightValue = document.getElementById('weightValue');
    weightValue.innerText = weightSlider.value;

    const heightSlider = document.getElementById('height');
    const heightValue = document.getElementById('heightValue');
    heightValue.innerText = heightSlider.value;
</script>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Weight a Minute - Result</title>
    <style>
        body {
            background: #1e3a8a;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1100px;
            margin: 40px auto;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        header { margin-bottom: 20px; text-align: center; }
        header h1 { font-size: 2.2rem; font-weight: 700; letter-spacing: 1px; }
        h2 { font-size: 2.0rem; margin: 16px 0 8px; text-align: center; }
        h3 { margin-top: 24px; font-weight: 700; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; }
        p { font-size: 1.05rem; margin: 8px 0; line-height: 1.4; }
        .alt-intakes { background: #2563eb; padding: 15px; border-radius: 10px; margin-top: 15px; text-align: left; }
        .alt-intakes p { margin: 8px 0; font-weight: 600; color: #dbeafe; }
        a { color: #93c5fd; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 25px; font-size: 1.05rem; }
        a:hover { text-decoration: underline; }
        canvas { margin-top: 20px; width: 100%; max-width: 100%; height: 300px; border-radius: 12px; background: #334eab; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .info-text { font-size: 0.95rem; color: #a5b4fc; margin-top: 12px; max-width: 900px; margin-left: auto; margin-right: auto; line-height: 1.4; text-align: center; }

        /* New two-column layout */
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; margin-top: 20px; }
        .panel { background: rgba(37, 99, 235, 0.25); padding: 16px; border-radius: 12px; }
        .warning { margin-top: 8px; padding: 10px; border-radius: 8px; background: #991b1b; color: #fde68a; font-weight: 700; }

        /* Small screens */
        @media (max-width: 900px) {
          .two-col { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <h1>Weight a Minute</h1>
    </header>

    <p style="text-align:center">To achieve your target weight loss of <strong>{{ weight_loss_goal }} kg</strong>, you should consume approximately:</p>
    <h2>{{ calorie_intake }} kcal/day</h2>
    {% if calorie_intake <= 600 %}
      <div class="warning">600 kcal shown. Any lower is unsafe. Increase calories or extend the timeline.</div>
    {% endif %}

    <h3>Alternatively (edit weeks to see changes)</h3>
    <div class="alt-intakes">
        <label for="alt_weeks">Number of weeks:</label>
        <input type="number" id="alt_weeks" min="1" max="52" value="{{ weeks_goal }}" />

        <p>To lose <strong>1 kg</strong>: ~ <strong id="cal1">{{ calorie_intake_1kg }}</strong> kcal/day</p>
        <p>To lose <strong>2 kg</strong>: ~ <strong id="cal2">{{ calorie_intake_2kg }}</strong> kcal/day</p>
        <div id="altWarn" class="warning" style="display:none;"></div>
    </div>

    <canvas id="weightLossChart"></canvas>

    <!-- Side-by-side: Muscle building on left, Pure Fat Loss on right -->
    <div class="two-col">
      <div class="panel">
        <h3>Muscle Building Nutrition</h3>
        <p><strong>Calories:</strong> {{ muscle_calories }} kcal/day</p>
        <p><strong>Protein:</strong> {{ protein_grams }} g/day</p>
        <p><strong>Carbohydrates:</strong> {{ carbs_grams }} g/day</p>
        <p><strong>Fats:</strong> {{ fats_grams }} g/day</p>
        <p class="info-text" style="text-align:left">Protein at 2 g/kg. Fats at 25% of calories. Carbs fill the remainder.</p>
      </div>

      <div class="panel">
        <h3>Pure Fat Loss, Get Lean</h3>
        <p>Presets by weekly loss. Uses TDEE and converts kg to daily deficit.</p>
        <div id="fatLossList"></div>
        <div id="fatLossWarn" class="warning" style="display:none;"></div>
      </div>
    </div>

    <p class="info-text">
        The charts show calorie targets for different deficits and a muscle plan that matches calories to macros.
    </p>
    <p class="info-text">
        For personalised advice, speak to a qualified professional.
    </p>

    <a href="/">&#8592; Calculate Again</a>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Chart 1
        const ctxWL = document.getElementById('weightLossChart').getContext('2d');
        const baseCalorie = {{ tdee }};
        const baselineDeficitRate = 0.15;
        const deficitRates = [0, 0.075, 0.15, 0.225, 0.30];
        const labelsWL = ['No Deficit', '7.5% Deficit', '15% Deficit', '22.5% Deficit', '30% Deficit'];
        const caloriesWL = deficitRates.map(r => Math.round(baseCalorie * (1 - r)));
        const weightLossKg = deficitRates.map(r => ((r / baselineDeficitRate) * 1).toFixed(2));

        new Chart(ctxWL, {
            type: 'line',
            data: {
                labels: labelsWL,
                datasets: [{
                    label: 'Calorie Intake (kcal/day)',
                    data: caloriesWL,
                    borderColor: '#93c5fd',
                    backgroundColor: 'rgba(147, 197, 253, 0.4)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    borderWidth: 3
                },{
                    label: 'Estimated Weight Loss (kg)',
                    data: weightLossKg,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.4)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    borderWidth: 3,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                stacked: false,
                scales: {
                    y: { type: 'linear', position: 'left', title: { display: true, text: 'Calories (kcal/day)', color: '#93c5fd', font: { size: 14 } },
                         ticks: { color: '#93c5fd' }, min: Math.min(...caloriesWL) * 0.9, max: Math.max(...caloriesWL) * 1.05 },
                    y1:{ type: 'linear', position: 'right', title: { display: true, text: 'Weight Loss (kg)', color: '#fbbf24', font: { size: 14 } },
                         ticks: { color: '#fbbf24' }, grid: { drawOnChartArea: false }, min: 0, max: 2.5 }
                },
                plugins: { legend: { labels: { color: 'white', font: { size: 14 } } }, tooltip: { enabled: true, mode: 'nearest', intersect: false } }
            }
        });

        // Alternative weeks widget
        const tdee = {{ tdee | safe }};
        const bmr = {{ bmr | safe }};

        const weeksInput = document.getElementById('alt_weeks');
        const cal1El = document.getElementById('cal1');
        const cal2El = document.getElementById('cal2');
        const altWarn = document.getElementById('altWarn');

        function warnIfLow(intakes) {
            const has600 = intakes.some(v => v <= 600);
            if (has600) {
                altWarn.style.display = 'block';
                altWarn.textContent = '600 kcal shown. Any lower is unsafe. Increase calories or extend the timeline.';
            } else {
                altWarn.style.display = 'none';
            }
        }

        function updateAltWidget() {
            const weeks = parseFloat(weeksInput.value);
            if (!weeks || weeks < 1) return;
            const c1 = Math.max(600, Math.round(tdee - (7700 / (weeks * 7))));
            const c2 = Math.max(600, Math.round(tdee - ((2 * 7700) / (weeks * 7))));
            cal1El.textContent = c1;
            cal2El.textContent = c2;
            warnIfLow([c1, c2]);
        }
        updateAltWidget();
        weeksInput.addEventListener('input', updateAltWidget);

        // Pure Fat Loss panel presets
        const fatLossList = document.getElementById('fatLossList');
        const fatLossWarn = document.getElementById('fatLossWarn');

        function makeRow(label, kgPerWeek) {
            const dailyDef = (kgPerWeek * 7700) / 7;
            const target = Math.max(600, Math.round(tdee - dailyDef));
            const bmrFloor = Math.round(0.7 * bmr);
            const row = document.createElement('p');
            row.innerHTML = `<strong>${label}</strong>: ${target} kcal/day  <span style="opacity:.8">(${kgPerWeek} kg/week)</span>`;
            fatLossList.appendChild(row);
            return { target, bmrFloor };
        }

        function buildFatLoss() {
            fatLossList.innerHTML = '';
            const results = [
                makeRow('Gentle deficit', 0.25),
                makeRow('Moderate deficit', 0.50),
                makeRow('Aggressive deficit', 0.75),
                makeRow('Max aggressive', 1.00)
            ];
            const anyTooLow = results.some(r => r.target <= 600);
            if (anyTooLow) {
                fatLossWarn.style.display = 'block';
                fatLossWarn.textContent = 'One or more presets hit 600 kcal. Any lower is unsafe. Pick a smaller weekly loss or raise activity.';
            } else {
                fatLossWarn.style.display = 'none';
            }
        }
        buildFatLoss();
    </script>
</body>
</html>
"""

def calculate_bmr(age, weight, height, gender):
    # Keep same base formula you used for TDEE
    if gender == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(age, weight, height, gender, activity_level):
    bmr = calculate_bmr(age, weight, height, gender)
    tdee = bmr * activity_level
    return bmr, tdee

@app.route('/', methods=['GET', 'POST'] )
def index():
    if request.method == 'POST':
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        gender = request.form['gender']
        activity_level = float(request.form['activity_level'])
        weight_loss_goal = float(request.form['weight_loss_goal'])
        weeks_goal = int(request.form['weeks_goal'])

        # BMR and TDEE
        bmr, tdee = calculate_tdee(age, weight, height, gender, activity_level)

        # Daily deficit across timeframe
        deficit_per_day = (weight_loss_goal * 7700) / (weeks_goal * 7)
        calorie_intake = max(600, tdee - deficit_per_day)

        # Alternatives 1 kg and 2 kg over the chosen weeks
        calorie_intake_1kg = max(600, tdee - (7700 / (weeks_goal * 7)))
        calorie_intake_2kg = max(600, tdee - ((2 * 7700) / (weeks_goal * 7)))

        # Muscle building target and macros that match calories
        muscle_calories = int(round(tdee * 1.10))
        protein_grams = round(weight * 2.0)
        fats_kcal = 0.25 * muscle_calories
        fats_grams = round(fats_kcal / 9)
        protein_kcal = protein_grams * 4
        remaining_kcal = max(0, muscle_calories - protein_kcal - fats_kcal)
        carbs_grams = round(remaining_kcal / 4)

        health_fact = random.choice(HEALTH_FACTS)

        return render_template_string(
            RESULT_HTML,
            calorie_intake=int(round(calorie_intake)),
            calorie_intake_1kg=int(round(calorie_intake_1kg)),
            calorie_intake_2kg=int(round(calorie_intake_2kg)),
            weight_loss_goal=weight_loss_goal,
            tdee=int(round(tdee)),
            bmr=int(round(bmr)),
            muscle_calories=muscle_calories,
            protein_grams=protein_grams,
            carbs_grams=carbs_grams,
            fats_grams=fats_grams,
            health_fact=health_fact,
            weeks_goal=weeks_goal
        )
    else:
        health_fact = random.choice(HEALTH_FACTS)
        return render_template_string(INDEX_HTML, health_fact=health_fact)

if __name__ == '__main__':
    app.run(port= 5002, debug=True)
