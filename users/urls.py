from django.urls import path

from users import views


urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name="login"),
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    path('add-new/', views.AddNewMemberAPIView.as_view(), name="add-new"),
    path('profile/', views.ProfileAPIView.as_view(), name="profile"),
    path('get-all/', views.GetAllMembers.as_view(), name="get-all-members"),
    path('<int:user_id>/', views.GetIndividualMember.as_view(), name="get-individual-members"),
    path('activate-or-deactivate/', views.ActivateOrDeactivateMember.as_view(), name="activate-or-deactivate-member"),
    path('update/<int:member_id>/', views.UpdateMember.as_view(), name="update-member")
]