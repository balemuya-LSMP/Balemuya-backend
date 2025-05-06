from .packages import *

class CategoryListCreateView(APIView):
    
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CategoryDetailView(APIView):
    def get_object(self, category_id):
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise NotFound(detail="Category not found")

    def patch(self, request, category_id):
        category = self.get_object(category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id):
        category = self.get_object(category_id)
        
        category.delete()
        return Response({'detail': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class StatisticsView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def get(self, request):
        if not request.user.user_type == 'admin':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        # User Statistics
        user_statistics = {
            "total_users": User.objects.filter(is_active=True).count(),
            "total_professionals": Professional.objects.filter(user__is_active=True).count(),
            "total_customers": Customer.objects.filter(user__is_active=True).count(),
            "total_admins": Admin.objects.filter(user__is_active=True).count(),
            "blocked_users": User.objects.filter(is_blocked=True).count(),
            "blocked_professionals": Professional.objects.filter(user__is_blocked=True).count(),
            "blocked_customers": Customer.objects.filter(user__is_blocked=True).count(),
            "blocked_admins": Admin.objects.filter(user__is_blocked=True).count(),
            "verified_professionals": Professional.objects.filter(is_verified=True).count(),
            "available_professionals": Professional.objects.filter(is_available=True).count(),
        }

        # Service Statistics
        service_statistics = {
            "total_services": ServicePost.objects.count(),
            "completed_services": ServicePost.objects.filter(status='completed').count(),
            "booked_services": ServicePost.objects.filter(status='booked').count(),
            "active_services": ServicePost.objects.filter(status='active').count(),
        }

        # Booking Statistics
        booking_statistics = {
            "total_bookings": ServiceBooking.objects.count(),
            "pending_bookings": ServiceBooking.objects.filter(status='pending').count(),
            "completed_bookings": ServiceBooking.objects.filter(status='completed').count(),
            "canceled_bookings": ServiceBooking.objects.filter(status='canceled').count(),
        }

        # Feedback and Complaint Statistics
        feedback_statistics = {
            "total_feedbacks": Feedback.objects.count(),
            "total_complains": Complain.objects.count(),
            "resolved_complains": Complain.objects.filter(status=True).count(),
            "unresolved_complains": Complain.objects.filter(status=False).count(),
        }

        # Financial Statistics
        total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue_stats = (
            Payment.objects
            .filter(payment_status='completed')
            .annotate(month=TruncMonth('payment_date'))
            .values('month')
            .annotate(
                total_revenue=Sum('amount'), 
                payment_count=Count('id')
            )
            .order_by('month')
        )
        monthly_revenue_stats_list = list(monthly_revenue_stats)
        
        monthly_subscription_plan_stats = (
                SubscriptionPlan.objects
                .annotate(month=TruncMonth('start_date'))  
                .values('month')
                .annotate(plan_count=Count('id'))
                .order_by('month')
            )

        monthly_subscription_plan_stats_list = list(monthly_subscription_plan_stats)
        number_of_gold_subscribers = SubscriptionPlan.objects.filter(plan_type='gold').count()
        number_of_dimond_subscribers = SubscriptionPlan.objects.filter(plan_type='dimond').count()
        number_of_silver_subscribers = SubscriptionPlan.objects.filter(plan_type='silver').count()

        # User Join Statistics
        monthly_user_stats = (
            User.objects
            .annotate(month=TruncMonth('date_joined'))
            .values('month')
            .annotate(user_count=Count('id'))
            .order_by('month')
        )
        monthly_user_stats_list = list(monthly_user_stats)
        

        # Prepare the final response
        response_data = {
            "user_statistics": user_statistics,
            "service_statistics": service_statistics,
            "booking_statistics": booking_statistics,
            "feedback_statistics": feedback_statistics,
            "financial_statistics": {
                "total_revenue": total_revenue,
                "number_of_gold_subscribers":number_of_gold_subscribers,
                "number_of_dimond_subscribers":number_of_dimond_subscribers,
                "number_of_silver_subscribers":number_of_silver_subscribers,
                "monthly_revenue_stats": monthly_revenue_stats_list,
                "monthly_subscription_plan_stats_list":monthly_subscription_plan_stats_list
            },
            "monthly_user_stats": monthly_user_stats_list,
        }

        return Response(response_data, status=status.HTTP_200_OK)         
         
     

class AdminServicePostReportListView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def get(self, request):
        reports = ServicePostReport.objects.select_related('service_post', 'reporter').all()
        serializer = ServicePostReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    
class AdminDeleteReportedPostView(APIView):
    permission_classes = [IsAdmin,IsAuthenticated]

    def delete(self, request, service_post_id):
        try:
            post = ServicePost.objects.select_related('customer__user').get(id=service_post_id)
        except ServicePost.DoesNotExist:
            return Response({'detail': 'Service post not found'}, status=status.HTTP_404_NOT_FOUND)

        customer = post.customer
        user = customer.user

        # Delete the post
        post.delete()
        
        return Response({
            'detail': f'Post deleted. User has {customer.report_count} reports.'
        }, status=status.HTTP_200_OK)
