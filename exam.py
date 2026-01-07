#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime


def show_summary(result_data):
    """Display exam result summary."""
    print(f"\n{'='*60}")
    print(f"Exam completed: {result_data['exam_name']}")
    print(f"Score: {result_data['score']:.1f}/10")
    print(f"{'='*60}\n")
    print(f"{'Question':<50} {'Type':<18} {'Your Answer':<15} {'Correct?'}")
    print("-" * 100)
    
    for r in result_data['results']:
        answer_str = str(r['user_answer'])
        correct_str = '✓' if r['correct'] else ('✗' if r['correct'] is not None else 'N/A')
        question_text = r['question'][:47] + '...' if len(r['question']) > 50 else r['question']
        print(f"{question_text:<50} {r['type']:<18} {answer_str:<15} {correct_str}")


def cmd_show_exams():
    """List, select and run an exam, then save results."""
    exams_dir = "exams"
    
    if not os.path.exists(exams_dir):
        print("No exams directory found")
        return
    
    exam_files = [f for f in os.listdir(exams_dir) if f.endswith('.json')]
    
    if not exam_files:
        print("No exams found")
        return
    
    print("Available exams:")
    for i, filename in enumerate(exam_files, 1):
        print(f"{i}. {filename}")
    
    choice = input("\nSelect exam number: ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(exam_files):
            print("Invalid selection")
            return
    except ValueError:
        print("Invalid input")
        return
    
    exam_path = os.path.join(exams_dir, exam_files[idx])
    
    with open(exam_path, 'r', encoding='utf-8') as f:
        exam = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"Exam: {exam['name']}")
    print(f"Description: {exam['description']}")
    print(f"{'='*60}\n")
    
    results = []
    
    for q_num, question in enumerate(exam['questions'], 1):
        print(f"\nQuestion {q_num}/{len(exam['questions'])}:")
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
            for i, opt in enumerate(question['options']):
                print(f"  {i}. {opt['text']}")
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
            for i, opt in enumerate(question['options']):
                print(f"  {i}. {opt['text']}")
            user_input = input("Select option numbers (comma-separated): ").strip()
            try:
                user_answer = [int(x.strip()) for x in user_input.split(',')]
                correct_answers = [i for i, opt in enumerate(question['options']) if opt['correct']]
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
            print("\n✓ Correct")
        elif last_result['correct'] is False:
            print("\n✗ Incorrect")

        print(f"Explanation: {question['explanation']}")
    
    # Calculate score
    gradable_questions = [r for r in results if r['correct'] is not None]
    correct_count = sum(1 for r in gradable_questions if r['correct'])
    total_questions = len(gradable_questions)
    score = (correct_count / total_questions * 10) if total_questions > 0 else 0
    
    # Save result
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"{exam['name'].replace(' ', '_')}_{timestamp}.json"
    result_path = os.path.join("results", result_filename)
    
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
    results_dir = "results"
    
    if not os.path.exists(results_dir):
        print("No results directory found")
        return
    
    result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    
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
    
    result_path = os.path.join(results_dir, result_files[idx])
    
    with open(result_path, 'r', encoding='utf-8') as f:
        result_data = json.load(f)
    
    show_summary(result_data)

def show_help():
    print("Usage: exam.py <command>")
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
