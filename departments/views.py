#from django.shortcuts import render
#
## Create your views here.
#
## departments/views.py
#
#from django.http import HttpResponse
#
#def create_department_view(request):
#    return HttpResponse("Create Department Page")
#
#def list_departments_view(request):
#    return HttpResponse("List of Departments")
#
#def update_department_view(request, dept_id):
#    return HttpResponse(f"Update Department {dept_id}")
#
#def delete_department_view(request, dept_id):
#    return HttpResponse(f"Delete Department {dept_id}")
#
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import add_department, delete_department, edit_department, get_departments_for_hospital
from .serializers import DepartmentSerializer

class DepartmentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hospital_id = request.query_params.get("hospital_id")
        if not hospital_id:
            return Response({"error": "hospital_id required"}, status=status.HTTP_400_BAD_REQUEST)
        depts = get_departments_for_hospital(hospital_id)
        return Response(DepartmentSerializer(depts, many=True).data)

    def post(self, request):
        data = request.data
        dept = add_department(
            hospital_id=data["hospital_id"],
            name=data["name"],
            description=data.get("description", ""),
            head_doctor_id=data.get("head_doctor_id")
        )
        return Response(DepartmentSerializer(dept).data, status=status.HTTP_201_CREATED)

class DepartmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, dept_id):
        dept = edit_department(dept_id, **request.data)
        return Response(DepartmentSerializer(dept).data)

    def delete(self, request, dept_id):
        hospital_id = request.data.get("hospital_id")
        name = request.data.get("name")
        delete_department(hospital_id, name)
        return Response(status=status.HTTP_204_NO_CONTENT)
