from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from CargoDelivery import settings
from apps.company.forms import WorkerProfileForm, WarehouseForm, TransportForm, SendingForm, ApplicationManageForm, \
    TransitPointForm
from apps.company.models import WorkerProfile, Company
from apps.main.models import Warehouse, Transport, Sending, Application, Order, TransitPoint


class CreateWorkerProfile(LoginRequiredMixin, CreateView):
    """
    View for creation of transport company worker
    (only users with owner accounts can make this)
    """
    model = WorkerProfile
    template_name = 'company/forms/create_workerprofile_form.html'
    form_class = WorkerProfileForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listworkers')

    def form_valid(self, form):
        """
        Set company of worker same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class UpdateWorkerProfile(LoginRequiredMixin, UpdateView):
    """
    View for updating of transport company worker
    (only users with owner accounts can make this)
    """
    model = WorkerProfile
    template_name = 'company/forms/update_workerprofile_form.html'
    form_class = WorkerProfileForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listworkers')

    def form_valid(self, form):
        """
        Set company of worker same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class DeleteWorkerProfile(LoginRequiredMixin, DeleteView):
    """
    View for updating of transport company worker
    (only users with owner accounts can make this)
    """
    model = WorkerProfile
    template_name = 'company/forms/delete_workerprofile_form.html'
    success_url = reverse_lazy('company:listworkers')


class WorkerProfileList(LoginRequiredMixin, ListView):
    """
    View for list all companies workers
    """
    model = WorkerProfile
    paginate_by = settings.PAGINATION_SIZE
    template_name = 'company/workers.html'

    def get_queryset(self):
        """
        Show only workers of companies same as company of creator
        :return:
        """
        try:
            queryset = WorkerProfile.objects.filter(company__workerprofile__user=self.request.user)
        except Exception:
            raise Http404
        else:
            return queryset


class WarehouseList(LoginRequiredMixin, ListView):
    """
    View for list all companies warehouses
    """
    model = Warehouse
    paginate_by = settings.PAGINATION_SIZE
    template_name = 'company/warehouses.html'

    def get_queryset(self):
        """
        Show only warehouses of companies same as company of creator
        :return:
        """
        try:
            queryset = Warehouse.objects.filter(company__workerprofile__user=self.request.user)
        except Exception:
            raise Http404
        else:
            return queryset


class CreateWarehouse(LoginRequiredMixin, CreateView):
    """
    View for creation of transport company warehouse
    (only users with owner accounts can make this)
    """
    model = Warehouse
    template_name = 'company/forms/create_form.html'
    form_class = WarehouseForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listwarehouse')

    def form_valid(self, form):
        """
        Set company of warehouse same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class UpdateWarehouse(LoginRequiredMixin, UpdateView):
    """
    View for updating of transport company warehouse
    (only users with owner accounts can make this)
    """
    model = Warehouse
    template_name = 'company/forms/update_form.html'
    form_class = WarehouseForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listwarehouse')

    def form_valid(self, form):
        """
        Set company of warehouse same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class DeleteWarehouse(LoginRequiredMixin, DeleteView):
    """
    View for updating of transport company warehouse
    (only users with owner accounts can make this)
    """
    model = Warehouse
    template_name = 'company/forms/delete_warehouse_form.html'
    success_url = reverse_lazy('company:listwarehouse')


class CreateTransport(LoginRequiredMixin, CreateView):
    """
    View for transport creation
    (only users with owner accounts can make this)
    """
    model = Transport
    template_name = 'company/forms/create_form.html'
    form_class = TransportForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listtransport')

    def form_valid(self, form):
        """
        Set company of transport same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class TransportList(LoginRequiredMixin, ListView):
    """
    View for list all companies transport
    """
    model = Transport
    paginate_by = settings.PAGINATION_SIZE
    template_name = 'company/transports.html'

    def get_queryset(self):
        """
        Show only transport of companies same as company of creator
        :return:
        """
        try:

            queryset = Transport.objects.filter(company__workerprofile__user=self.request.user)
        except Exception:
            raise Http404
        else:
            return queryset


class UpdateTransport(LoginRequiredMixin, UpdateView):
    """
    View for updating of transport

    """
    model = Transport
    template_name = 'company/forms/update_form.html'
    form_class = TransportForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listtransport')

    def form_valid(self, form):
        """
        Set company of transport same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class DeleteTransport(LoginRequiredMixin, DeleteView):
    """
    View for updating of transport company warehouse

    """
    model = Transport
    template_name = 'company/forms/delete_transport_form.html'
    success_url = reverse_lazy('company:listtransport')


class CreateSending(LoginRequiredMixin, CreateView):
    """
    View for sending creation

    """
    model = Sending
    template_name = 'company/forms/create_form.html'
    form_class = SendingForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listsending')

    def get_form_kwargs(self):
        kwargs = super(CreateSending, self).get_form_kwargs()
        user = self.request.user

        if user:
            kwargs['user'] = user

        return kwargs

    def form_valid(self, form):
        """
        Set company of sending same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)

        return super().form_valid(form)


class UpdateSending(LoginRequiredMixin, UpdateView):
    """
    View for updating of sending

    """
    model = Sending
    template_name = 'company/forms/update_form.html'
    form_class = SendingForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listsending')

    def get_form_kwargs(self):
        kwargs = super(UpdateSending, self).get_form_kwargs()
        user = self.request.user

        if user:
            kwargs['user'] = user

        return kwargs

    def form_valid(self, form):
        """
        Set company of sending same as company of creator
        :param form:
        :return:
        """
        form.instance.company = Company.objects.get(workerprofile__user=self.request.user)
        return super().form_valid(form)


class DeleteSending(LoginRequiredMixin, DeleteView):
    """
    View for deleting of transport company sending

    """
    model = Sending
    template_name = 'company/forms/delete_sending_form.html'
    success_url = reverse_lazy('company:listsending')


class SendingList(LoginRequiredMixin, ListView):
    """
    View for list all companies sendings
    """
    model = Sending
    paginate_by = settings.PAGINATION_SIZE
    template_name = 'company/sendings.html'

    def get_queryset(self):
        """
        Show only sendings of companies same as company of creator
        :return:
        """
        try:
            queryset = Sending.objects.filter(company__workerprofile__user=self.request.user)
        except Exception:
            raise Http404
        else:
            return queryset


class SendingDetail(LoginRequiredMixin, DeleteView):
    """
    View for detail of sending
    """

    model = Sending
    template_name = 'company/sending_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transit_points = TransitPoint.objects.filter(sending=self.object)
        context['transit_points'] = transit_points
        return context


class ApplicationListManage(LoginRequiredMixin, ListView):
    """
    View for list all application for that company
    """
    model = Application
    paginate_by = settings.PAGINATION_SIZE
    template_name = 'company/applications.html'
    success_url = reverse_lazy('company:listapplicationmanage')

    def get_queryset(self):
        """
        Show only applications for companies same as company of creator
        :return:
        """
        try:
            queryset = Application.objects.filter(
                sending__company__workerprofile__user=self.request.user)
        except Exception:
            raise Http404
        else:
            return queryset


class UpdateApplicationManage(LoginRequiredMixin, UpdateView):
    """
    View for updating of application for companies
    """
    model = Application
    template_name = 'company/forms/update_application_form.html'
    form_class = ApplicationManageForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listapplicationmanage')

    def form_valid(self, form):
        sending = self.object.sending
        order = self.object.order
        if order not in sending.orders.all() and self.object.status == 'CONF':
            sending.orders.add(order)
        elif order in sending.orders.all() and self.object.status == 'DECL':
            sending.orders.remove(order)
        elif order in sending.orders.all() and self.object.status == 'WAIT':
            sending.orders.remove(order)
        sending.save()
        return super().form_valid(form)


class OrderDetailManage(LoginRequiredMixin, DetailView):
    """
    View for details of user's order.
    Only for company workers
    """
    model = Order
    template_name = 'company/order_detail_manage.html'

    def get_context_data(self, **kwargs):
        """
        Checks if order application belongs to company
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        application = Application.objects.get(order=self.object)
        if application.sending.company == self.request.user.workerprofile.company:
            context['application'] = application
        return context


class CreateTransitPoint(LoginRequiredMixin, CreateView):
    """
    View for creation of transit point for sendings
    (for companies)
    """
    model = TransitPoint
    template_name = 'company/forms/create_form.html'
    form_class = TransitPointForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listsending')

    def get_form_kwargs(self):
        kwargs = super(CreateTransitPoint, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Substitution of selected sending
        :param form:
        :return:
        """
        form.instance.sending = Sending.objects.get(pk=self.kwargs['pk'])
        if self.request.user.workerprofile.company == form.instance.sending.company:
            return super().form_valid(form)
        else:
            raise Http404('You can not do it')


class DeleteTransitPoint(LoginRequiredMixin, DeleteView):
    """
    View for deleting of transport company transit point

    """
    model = TransitPoint
    template_name = 'company/forms/delete_transitpoint_form.html'
    success_url = reverse_lazy('company:listsending')


class UpdateTransitPoint(LoginRequiredMixin, UpdateView):
    """
    View for updating of transit point

    """
    model = TransitPoint
    template_name = 'company/forms/update_transitpoint_form.html'
    form_class = TransitPointForm
    login_url = 'login/'
    success_url = reverse_lazy('company:listsending')

    def get_form_kwargs(self):
        kwargs = super(UpdateTransitPoint, self).get_form_kwargs()
        user = self.request.user
        if user:
            kwargs['user'] = user

        return kwargs

    def form_valid(self, form):
        """
        Set sending same as editing
        :param form:
        :return:
        """
        form.instance.sending = Sending.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)
