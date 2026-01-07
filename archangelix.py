#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime

EXAMS_DIR = "exams"
RESULTS_DIR = "results"


def show_summary(result_data):
    """Display exam result summary."""
    
    print(f"\n{'='*60}")
    print(f"Exam completed: {result_data['exam_name']}")
    print(f"Score: {result_data['score']:.1f}/10")
    print(f"{'='*60}\n")
    print(f"{'Question':<50} {'Type':<18} {'Your Answer':<15} {'Correct?'}")
    print("-" * 100)

    for r in result_data['results']:
        answer = str(r['user_answer'])
        correctness = '✓' if r['correct'] else (
            '✗' if r['correct'] is not None else 'N/A')
        question = r['question'][:47] + \
            '...' if len(r['question']) > 50 else r['question']
        print(
            f"{question:<50} {r['type']:<18} {answer:<15} {correctness}")


def cmd_show_exams():
    """List, select and run an exam, then save results."""

    if not os.path.exists(EXAMS_DIR):
        print("No exams directory found")
        return

    exams = [f for f in os.listdir(EXAMS_DIR) if f.endswith('.json')]

    if not exams:
        print("No exams found")
        return

    print("Available exams:")
    for exam_index, filename in enumerate(exams, 1):
        print(f"{exam_index}. {filename}")

    choice = input("\nSelect exam number: ").strip()

    try:
        selected_index = int(choice) - 1
        if selected_index < 0 or selected_index >= len(exams):
            print("Invalid selection")
            return
    except ValueError:
        print("Invalid input")
        return

    exam_path = os.path.join(EXAMS_DIR, exams[selected_index])

    with open(exam_path, 'r', encoding='utf-8') as f:
        exam = json.load(f)

    print(f"\n{'='*60}")
    print(f"Exam: {exam['name']}")
    print(f"Description: {exam['description']}")
    print(f"{'='*60}")

    results = []

    for question_index, question in enumerate(exam['questions'], 1):
        print(f"\nQuestion {question_index}/{len(exam['questions'])}:")
        print(question['question'])

        if question['type'] == 'yes_no':
            user_input = input("Answer (yes/no): ").strip().lower()
            user_answer = 'yes' if user_input in ['yes', 'y'] else 'no'
            correct = user_answer == 'yes'
            results.append({
                'question': question['question'],
                'type': question['type'],
                'user_answer': user_answer,
                'correct': correct,
                'explanation': question['explanation']
            })

        elif question['type'] == 'single_choice':
            for option_index, option in enumerate(question['options']):
                print(f"  {option_index}. {option['text']}")
            user_input = input("Select option number: ").strip()
            try:
                user_answer = int(user_input)
                correct = question['options'][user_answer]['correct']
            except (ValueError, IndexError):
                user_answer = -1
                correct = False

            results.append({
                'question': question['question'],
                'type': question['type'],
                'options': question['options'],
                'user_answer': user_answer,
                'correct': correct,
                'explanation': question['explanation']
            })

        elif question['type'] == 'multiple_choice':
            for exam_index, option in enumerate(question['options']):
                print(f"  {exam_index}. {option['text']}")
            user_input = input(
                "Select option numbers (comma-separated): ").strip()
            try:
                user_answer = [int(x.strip()) for x in user_input.split(',')]
                correct_answers = [option_index for option_index, option in enumerate(
                    question['options']) if option['correct']]
                correct = sorted(user_answer) == sorted(correct_answers)
            except (ValueError, IndexError):
                user_answer = []
                correct = False

            results.append({
                'question': question['question'],
                'type': question['type'],
                'options': question['options'],
                'user_answer': user_answer,
                'correct': correct,
                'explanation': question['explanation']
            })

        elif question['type'] == 'free_text':
            user_answer = input("Your answer: ").strip()
            correct_answer = question.get('correct_answer', '').strip().lower()
            user_answer_normalized = user_answer.lower()
            correct = correct_answer in user_answer_normalized if correct_answer else True
            results.append({
                'question': question['question'],
                'type': question['type'],
                'user_answer': user_answer,
                'correct': correct,
                'explanation': question['explanation']
            })

        # Show if answer was correct
        last_result = results[-1]
        if last_result['correct'] is True:
            print("✓ Correct")
        elif last_result['correct'] is False:
            print("✗ Incorrect")

        print(f"Explanation: {question['explanation']}")

    # Calculate score
    gradable_questions = [r for r in results if r['correct'] is not None]
    correct_count = sum(1 for r in gradable_questions if r['correct'])
    total_questions = len(gradable_questions)
    score = (correct_count / total_questions *
             10) if total_questions > 0 else 0

    # Save result
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"{exam['name'].replace(' ', '_')}_{timestamp}.json"
    result_path = os.path.join(RESULTS_DIR, result_filename)

    result_data = {
        'exam_name': exam['name'],
        'exam_description': exam['description'],
        'timestamp': datetime.now().isoformat(),
        'score': score,
        'total_questions': len(exam['questions']),
        'correct_answers': correct_count,
        'results': results
    }

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    # Load and show summary
    with open(result_path, 'r', encoding='utf-8') as f:
        saved_result = json.load(f)

    show_summary(saved_result)


def cmd_show_results():
    """List and show summary of saved exam results."""

    if not os.path.exists(RESULTS_DIR):
        print("No results directory found")
        return

    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]

    if not result_files:
        print("No saved results found")
        return

    print("Saved results:")
    for i, filename in enumerate(result_files, 1):
        print(f"{i}. {filename}")

    choice = input("\nSelect result number: ").strip()

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(result_files):
            print("Invalid selection")
            return
    except ValueError:
        print("Invalid input")
        return

    result_path = os.path.join(RESULTS_DIR, result_files[idx])

    with open(result_path, 'r', encoding='utf-8') as f:
        result_data = json.load(f)

    show_summary(result_data)


def show_help():
    print("Usage: archangelix.py <command>")
    print("Commands:")
    print("  show_exams   - List, select and run an exam")
    print("  show_results - Show saved exam results")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].strip().lower()

    if command == "show_exams":
        cmd_show_exams()
    elif command == "show_results":
        cmd_show_results()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
