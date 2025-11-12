from rest_framework import serializers
from .models import Project, Folder, TestCase

class ProjectSerializer(serializers.ModelSerializer):
    folders_count = serializers.SerializerMethodField()
    test_cases_count = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'author', 'author_name',
            'created_at', 'updated_at', 'level', 
            'folders_count', 'test_cases_count'
        ]
        read_only_fields = ('author', 'created_at', 'updated_at', 'level')
    
    def get_folders_count(self, obj):
        return obj.folders.count()
    
    def get_test_cases_count(self, obj):
        return obj.test_cases.count()
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class FolderSerializer(serializers.ModelSerializer):
    subfolders_count = serializers.SerializerMethodField()
    test_cases_count = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    parent_folder_name = serializers.CharField(source='parent_folder.name', read_only=True, allow_null=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Folder
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at', 'level', 'project')
    
    def get_subfolders_count(self, obj):
        return obj.subfolders.count()
    
    def get_test_cases_count(self, obj):
        return obj.test_cases.count()
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class TestCaseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True, allow_null=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = TestCase
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at', 'level')
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
