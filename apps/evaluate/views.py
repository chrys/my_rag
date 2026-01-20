"""
Evaluate views for dataset generation and evaluation
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

# TODO: These imports are commented out as part of Flask-to-Django migration
# They should be replaced with Django API views
# from evaluate.llamaindex_dataset_generation import (
#     init_evaluation,
#     create_dummy_documents,
#     generate_dataset,
#     define_evaluators,
#     run_batch_evaluation,
# )
# from local_project_storage import get_local_project_storage
# from local_rag import get_rag_engine

from .models import EvaluationDataset, EvaluationResult


# TODO: These views are Flask-based and commented out as part of Django migration
# Use API views (apps/evaluate/api_views.py) instead for REST API access

# @require_http_methods(["POST"])
# @csrf_exempt
# def evaluate(request):
#     """Handle evaluation dataset generation"""
#     try:
#         data = json.loads(request.body)
#         store_id = data.get('store_id')
#         num_questions = data.get('num_questions', 10)
#         
#         if not store_id:
#             return JsonResponse({'error': 'Missing store_id'}, status=400)
#         
#         # Create or get evaluation dataset
#         dataset = EvaluationDataset.objects.create(
#             name=f"Dataset for {store_id}",
#             num_questions=num_questions
#         )
#         
#         try:
#             # Initialize evaluation
#             if store_id.startswith('local_'):
#                 rag_engine = get_rag_engine(store_id)
#                 
#                 # Generate dataset
#                 dataset.state = 'GENERATING'
#                 dataset.save()
#                 
#                 qa_pairs = generate_dataset(rag_engine, num_questions)
#                 
#                 dataset.qa_pairs = qa_pairs
#                 dataset.state = 'GENERATED'
#                 dataset.save()
#             else:
#                 return JsonResponse({'error': 'Evaluation not yet implemented for Google stores'}, status=400)
#             
#             return JsonResponse({
#                 'status': 'success',
#                 'dataset_id': dataset.id,
#                 'qa_pairs': qa_pairs
#             })
#         
#         except Exception as e:
#             dataset.state = 'FAILED'
#             dataset.error_message = str(e)
#             dataset.save()
#             raise
#     
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({'error': str(e)}, status=500)
