# Routing and view tests
import pytest
import random
from flask import url_for, current_app
from urlparse import urlparse
from .conftest import AC_DEPT
from ..app.utils import dept_choices
from ..app.main.choices import RACE_CHOICES, GENDER_CHOICES

from OpenOversight.app.main.forms import (FindOfficerIDForm, AssignmentForm,
                                          FaceTag, DepartmentForm,
                                          AddOfficerForm, AddUnitForm,
                                          EditOfficerForm)
from OpenOversight.app.auth.forms import (LoginForm, RegistrationForm,
                                          ChangePasswordForm, PasswordResetForm,
                                          PasswordResetRequestForm,
                                          ChangeEmailForm, ChangeDefaultDepartmentForm, EditUserForm)
from OpenOversight.app.models import (User, Face, Department, Unit, Officer,
                                      Image)


@pytest.mark.parametrize("route", [
    ('/'),
    ('/index'),
    ('/browse'),
    ('/find'),
    ('/about'),
    ('/tagger_find'),
    ('/privacy'),
    ('/submit'),
    ('/submit/department/1'),
    ('/label'),
    ('/department/1'),
    ('/officer/3'),
    ('/tutorial'),
    ('/auth/login'),
    ('/auth/register'),
    ('/auth/reset'),
    ('/complaint?officer_star=1901&officer_first_name=HUGH&officer_last_name=BUTZ&officer_middle_initial=&officer_image=static%2Fimages%2Ftest_cop2.png')
])
def test_routes_ok(route, client, mockdata):
    rv = client.get(route)
    assert rv.status_code == 200


# All login_required views should redirect if there is no user logged in
@pytest.mark.parametrize("route", [
    ('/auth/unconfirmed'),
    ('/sort/department/1'),
    ('/cop_face/department/1'),
    ('/image/1'),
    ('/image/tagged/1'),
    ('/tag/1'),
    ('/leaderboard'),
    ('/department/new'),
    ('/officer/new'),
    ('/unit/new'),
    ('/auth/logout'),
    ('/auth/confirm/abcd1234'),
    ('/auth/confirm'),
    ('/auth/change-password'),
    ('/auth/change-email'),
    ('/auth/change-email/abcd1234')
])
def test_route_login_required(route, client, mockdata):
    rv = client.get(route)
    assert rv.status_code == 302


# POST-only routes
@pytest.mark.parametrize("route", [
    ('/officer/3/assignment/new'),
    ('/tag/delete/1'),
    ('/image/classify/1/1')
])
def test_route_post_only(route, client, mockdata):
    rv = client.get(route)
    assert rv.status_code == 405


# def test_find_form_submission(client, mockdata):
#     with current_app.test_request_context():
#         form = FindOfficerForm()
#         assert form.validate() == True
#         rv = client.post(url_for('main.get_officer'), data=form.data, follow_redirects=False)
#         assert rv.status_code == 307
#         assert urlparse(rv.location).path == '/gallery'
#
#
# def test_bad_form(client, mockdata):
#     with current_app.test_request_context():
#         form = FindOfficerForm(dept='')
#         assert form.validate() == False
#         rv = client.post(url_for('main.get_officer'), data=form.data, follow_redirects=False)
#         assert rv.status_code == 307
#         assert urlparse(rv.location).path == '/find'
#
#
# def test_find_form_redirect_submission(client, session):
#     with current_app.test_request_context():
#         form = FindOfficerForm()
#         assert form.validate() == True
#         rv = client.post(url_for('main.get_officer'), data=form.data, follow_redirects=False)
#         assert rv.status_code == 200


def test_tagger_lookup(client, session):
    with current_app.test_request_context():
        form = FindOfficerIDForm(dept='')
        assert form.validate() is True
        rv = client.post(url_for('main.get_ooid'), data=form.data,
                         follow_redirects=False)
        assert rv.status_code == 307
        assert urlparse(rv.location).path == '/tagger_gallery'


def test_tagger_gallery(client, session):
    with current_app.test_request_context():
        form = FindOfficerIDForm(dept='')
        assert form.validate() is True
        rv = client.post(url_for('main.get_tagger_gallery'), data=form.data)
        assert rv.status_code == 200


def test_tagger_gallery_bad_form(client, session):
    with current_app.test_request_context():
        form = FindOfficerIDForm(badge='THIS IS NOT VALID')
        assert form.validate() is False
        rv = client.post(url_for('main.get_tagger_gallery'), data=form.data,
                         follow_redirects=False)
        assert rv.status_code == 307
        assert urlparse(rv.location).path == '/tagger_find'


def login_user(client):
    form = LoginForm(email='jen@example.org',
                     password='dog',
                     remember_me=True)
    rv = client.post(
        url_for('auth.login'),
        data=form.data,
        follow_redirects=False
    )
    return rv


def login_admin(client):
    form = LoginForm(email='redshiftzero@example.org',
                     password='cat',
                     remember_me=True)
    rv = client.post(
        url_for('auth.login'),
        data=form.data,
        follow_redirects=False
    )
    return rv


def login_ac(client):
    form = LoginForm(email='raq929@example.org',
                     password='horse',
                     remember_me=True)
    rv = client.post(
        url_for('auth.login'),
        data=form.data,
        follow_redirects=False
    )
    return rv


def test_valid_user_can_login(mockdata, client, session):
    with current_app.test_request_context():
        rv = login_user(client)
        assert rv.status_code == 302
        assert urlparse(rv.location).path == '/index'


def test_invalid_user_cannot_login(mockdata, client, session):
    with current_app.test_request_context():
        form = LoginForm(email='freddy@example.org',
                         password='bruteforce',
                         remember_me=True)
        rv = client.post(
            url_for('auth.login'),
            data=form.data
        )
        assert 'Invalid username or password.' in rv.data


def test_user_can_logout(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('auth.logout'),
            follow_redirects=True
        )
        assert 'You have been logged out.' in rv.data


def test_logged_in_user_can_access_sort_form(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('main.sort_images', department_id=1),
            follow_redirects=True
        )
        assert 'Do you see police officers in the photo' in rv.data


def test_user_can_access_profile(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('main.profile', username='test_user'),
            follow_redirects=True
        )
        assert 'test_user' in rv.data
        # User email should not appear
        assert 'User Email' not in rv.data
        # Toggle button should not appear for this non-admin user
        assert 'Toggle (Disable/Enable) User' not in rv.data


def test_admin_sees_toggle_button_on_profiles(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        rv = client.get(
            url_for('main.profile', username='test_user'),
            follow_redirects=True
        )
        assert 'test_user' in rv.data
        # User email should appear
        assert 'User Email' in rv.data
        # Admin should be able to see the Toggle button
        assert 'Toggle (Disable/Enable) User' in rv.data


def test_user_can_access_officer_profile(mockdata, client, session):
    with current_app.test_request_context():
        rv = client.get(
            url_for('main.officer_profile', officer_id=3),
            follow_redirects=True
        )
        assert 'Officer Detail' in rv.data


def test_user_can_access_officer_list(mockdata, client, session):
    with current_app.test_request_context():
        rv = client.get(
            url_for('main.list_officer', department_id=2)
        )

        assert 'Officers' in rv.data


def test_ac_can_access_admin_on_dept_officer_profile(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)
        officer = Officer.query.filter_by(department_id=AC_DEPT).first()

        rv = client.get(
            url_for('main.officer_profile', officer_id=officer.id),
            follow_redirects=True
        )
        assert 'Admin only' in rv.data


def test_ac_cannot_access_admin_on_non_dept_officer_profile(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)
        officer = Officer.query.except_(Officer.query.filter_by(department_id=AC_DEPT)).first()

        rv = client.get(
            url_for('main.officer_profile', officer_id=officer.id),
            follow_redirects=True
        )
        assert 'Admin only' not in rv.data


def test_admin_can_add_officer_badge_number(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        form = AssignmentForm(star_no='1234',
                              rank='COMMANDER')

        rv = client.post(
            url_for('main.add_assignment', officer_id=3),
            data=form.data,
            follow_redirects=True
        )

        assert 'Added new assignment' in rv.data


def test_ac_can_add_officer_badge_number_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        form = AssignmentForm(star_no='S1234',
                              rank='COMMANDER')
        officer = Officer.query.filter_by(department_id=AC_DEPT).first()

        rv = client.post(
            url_for('main.add_assignment', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        assert 'Added new assignment' in rv.data

        # test that assignment exists in database
        assignment = Officer.query.filter(Officer.assignments.any(star_no='S1234'))
        assert assignment is not None


def test_ac_cannot_add_non_dept_officer_badge(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        form = AssignmentForm(star_no='1234',
                              rank='COMMANDER')
        officer = Officer.query.except_(Officer.query.filter_by(department_id=AC_DEPT)).first()

        rv = client.post(
            url_for('main.add_assignment', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        assert rv.status_code == 403


def test_admin_can_edit_officer_badge_number(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        form = AssignmentForm(star_no='1234',
                              rank='COMMANDER')

        rv = client.post(
            url_for('main.officer_profile', officer_id=3),
            data=form.data,
            follow_redirects=True
        )

        form = AssignmentForm(star_no='12345')
        officer = Officer.query.filter_by(id=3).one()

        rv = client.post(
            url_for('main.edit_assignment', officer_id=officer.id,
                    assignment_id=officer.assignments[0].id,
                    form=form),
            data=form.data,
            follow_redirects=True
        )

        assert 'Edited officer assignment' in rv.data
        assert officer.assignments[0].star_no == '12345'


def test_ac_can_edit_officer_in_their_dept_badge_number(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        star_no = '1234'
        new_star_no = '12345'
        officer = Officer.query.filter_by(department_id=AC_DEPT).first()
        form = AssignmentForm(star_no=star_no,
                              rank='COMMANDER')

        rv = client.post(
            url_for('main.officer_profile', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        form = AssignmentForm(star_no=new_star_no)
        officer = Officer.query.filter_by(id=officer.id).one()

        rv = client.post(
            url_for('main.edit_assignment', officer_id=officer.id,
                    assignment_id=officer.assignments[0].id,
                    form=form),
            data=form.data,
            follow_redirects=True
        )

        assert 'Edited officer assignment' in rv.data
        assert officer.assignments[0].star_no == new_star_no


def test_ac_cannot_edit_officer_outside_their_dept_badge_number(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        star_no = '1234'
        new_star_no = '12345'
        officer = Officer.query.except_(Officer.query.filter_by(department_id=AC_DEPT)).first()
        form = AssignmentForm(star_no=star_no,
                              rank='COMMANDER')

        rv = client.post(
            url_for('main.officer_profile', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        form = AssignmentForm(star_no=new_star_no)
        officer = Officer.query.filter_by(id=officer.id).one()

        rv = client.post(
            url_for('main.edit_assignment', officer_id=officer.id,
                    assignment_id=officer.assignments[0].id,
                    form=form),
            data=form.data,
            follow_redirects=True
        )

        assert rv.status_code == 403


def test_user_can_view_submission(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('main.display_submission', image_id=1),
            follow_redirects=True
        )
        assert 'Image ID' in rv.data


def test_user_can_view_tag(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('main.display_tag', tag_id=1),
            follow_redirects=True
        )
        assert 'Tag' in rv.data


def test_admin_can_toggle_user(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        rv = client.post(
            url_for('main.toggle_user', uid=1),
            follow_redirects=True
        )
        assert 'Disabled' in rv.data


def test_ac_cannot_toggle_user(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        rv = client.post(
            url_for('main.toggle_user', uid=1),
            follow_redirects=True
        )
        assert rv.status_code == 403


def test_user_cannot_toggle_user(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.post(
            url_for('main.toggle_user', uid=1),
            follow_redirects=True
        )
        assert rv.status_code == 403


def test_admin_can_delete_tag(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        rv = client.post(
            url_for('main.delete_tag', tag_id=1),
            follow_redirects=True
        )
        assert 'Deleted this tag' in rv.data


def test_ac_can_delete_tag_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        tag = Face.query.filter(Face.officer.has(department_id=AC_DEPT)).first()
        tag_id = tag.id

        rv = client.post(
            url_for('main.delete_tag', tag_id=tag_id),
            follow_redirects=True
        )
        assert 'Deleted this tag' in rv.data

        # test tag was deleted from database
        deleted_tag = Face.query.filter_by(id=tag_id).first()
        assert deleted_tag is None


def test_ac_cannot_delete_tag_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        tag = Face.query.join(Face.officer, aliased=True).except_(Face.query.filter(Face.officer.has(department_id=AC_DEPT))).first()

        tag_id = tag.id

        rv = client.post(
            url_for('main.delete_tag', tag_id=tag_id),
            follow_redirects=True
        )
        assert rv.status_code == 403

        # test tag was not deleted from database
        deleted_tag = Face.query.filter_by(id=tag_id).first()
        assert deleted_tag is not None


def test_user_can_add_tag(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        officer = Image.query.filter_by(department_id=1).first()
        image = Image.query.filter_by(department_id=1).first()
        form = FaceTag(officer_id=officer.id,
                       image_id=image.id,
                       dataX=34,
                       dataY=32,
                       dataWidth=3,
                       dataHeight=33)

        rv = client.post(
            url_for('main.label_data', image_id=image.id),
            data=form.data,
            follow_redirects=True
        )
        assert 'Tag added to database' in rv.data


def test_user_is_redirected_to_correct_department_after_tagging(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        department_id = 2
        image = Image.query.filter_by(department_id=department_id, faces=None).first()
        print("FACES", image.faces)
        rv = client.get(
            url_for('main.complete_tagging', image_id=image.id, department_id=department_id),
            follow_redirects=True
        )
        department = Department.query.get(department_id)

        assert rv.status_code == 200
        assert department.name in rv.data.decode('utf-8')


def test_user_cannot_add_tag_if_it_exists(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        tag = Face.query.first()
        form = FaceTag(officer_id=tag.officer_id,
                       image_id=tag.img_id,
                       dataX=34,
                       dataY=32,
                       dataWidth=3,
                       dataHeight=33)

        rv = client.post(
            url_for('main.label_data', image_id=tag.img_id),
            data=form.data,
            follow_redirects=True
        )
        assert 'Tag already exists between this officer and image! Tag not added.' in rv.data


def test_user_cannot_tag_nonexistent_officer(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        tag = Face.query.first()
        form = FaceTag(officer_id=999999999999999999,
                       image_id=tag.img_id,
                       dataX=34,
                       dataY=32,
                       dataWidth=3,
                       dataHeight=33)

        rv = client.post(
            url_for('main.label_data', image_id=tag.img_id),
            data=form.data,
            follow_redirects=True
        )
        assert 'Invalid officer ID' in rv.data


def test_user_can_finish_tagging(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('main.complete_tagging', image_id=4),
            follow_redirects=True
        )
        assert 'Marked image as completed.' in rv.data


def test_user_can_view_leaderboard(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('main.leaderboard'),
            follow_redirects=True
        )
        assert 'Top Users by Number of Images Sorted' in rv.data


def test_user_cannot_register_with_existing_email(mockdata, client, session):
    with current_app.test_request_context():
        form = RegistrationForm(email='jen@example.org',
                                username='redshiftzero',
                                password='dog',
                                password2='dog')
        rv = client.post(
            url_for('auth.register'),
            data=form.data,
            follow_redirects=False
        )

        # Form will return 200 only if the form does not validate
        assert rv.status_code == 200
        assert 'Email already registered' in rv.data


def test_user_cannot_register_if_passwords_dont_match(mockdata, client, session):
    with current_app.test_request_context():
        form = RegistrationForm(email='freddy@example.org',
                                username='b_meson',
                                password='dog',
                                password2='cat')
        rv = client.post(
            url_for('auth.register'),
            data=form.data,
            follow_redirects=False
        )

        # Form will return 200 only if the form does not validate
        assert rv.status_code == 200
        assert 'Passwords must match' in rv.data


def test_user_can_register_with_legit_credentials(mockdata, client, session):
    with current_app.test_request_context():
        diceware_password = 'operative hamster perservere verbalize curling'
        form = RegistrationForm(email='jen@example.com',
                                username='redshiftzero',
                                password=diceware_password,
                                password2=diceware_password)
        rv = client.post(
            url_for('auth.register'),
            data=form.data,
            follow_redirects=True
        )

        assert 'A confirmation email has been sent to you.' in rv.data


def test_user_cannot_register_with_weak_password(mockdata, client, session):
    with current_app.test_request_context():
        form = RegistrationForm(email='jen@example.com',
                                username='redshiftzero',
                                password='weak',
                                password2='weak')
        rv = client.post(
            url_for('auth.register'),
            data=form.data,
            follow_redirects=True
        )

        assert 'A confirmation email has been sent to you.' not in rv.data


def test_user_can_get_a_confirmation_token_resent(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        rv = client.get(
            url_for('auth.resend_confirmation'),
            follow_redirects=True
        )

        assert 'A new confirmation email has been sent to you.' in rv.data


def test_user_can_get_password_reset_token_sent(mockdata, client, session):
    with current_app.test_request_context():
        form = PasswordResetRequestForm(email='jen@example.org')

        rv = client.post(
            url_for('auth.password_reset_request'),
            data=form.data,
            follow_redirects=True
        )

        assert 'An email with instructions to reset your password' in rv.data


def test_user_can_get_reset_password_with_valid_token(mockdata, client, session):
    with current_app.test_request_context():
        form = PasswordResetForm(email='jen@example.org',
                                 password='catdog',
                                 password2='catdog')
        user = User.query.filter_by(email='jen@example.org').one()
        token = user.generate_reset_token()

        rv = client.post(
            url_for('auth.password_reset', token=token),
            data=form.data,
            follow_redirects=True
        )

        assert 'Your password has been updated.' in rv.data


def test_user_cannot_reset_password_with_invalid_token(mockdata, client, session):
    with current_app.test_request_context():
        form = PasswordResetForm(email='jen@example.org',
                                 password='catdog',
                                 password2='catdog')
        token = 'beepboopbeep'

        rv = client.post(
            url_for('auth.password_reset', token=token),
            data=form.data,
            follow_redirects=True
        )

        assert 'Your password has been updated.' not in rv.data


def test_user_cannot_get_email_reset_token_sent_without_valid_password(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        form = ChangeEmailForm(email='jen@example.org',
                               password='dogdogdogdog')

        rv = client.post(
            url_for('auth.change_email_request'),
            data=form.data,
            follow_redirects=True
        )

        assert 'An email with instructions to confirm your new email' not in rv.data


def test_user_can_get_email_reset_token_sent_with_password(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        form = ChangeEmailForm(email='alice@example.org',
                               password='dog')

        rv = client.post(
            url_for('auth.change_email_request'),
            data=form.data,
            follow_redirects=True
        )

        assert 'An email with instructions to confirm your new email' in rv.data


def test_user_can_change_email_with_valid_reset_token(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        user = User.query.filter_by(email='jen@example.org').one()
        token = user.generate_email_change_token('alice@example.org')

        rv = client.get(
            url_for('auth.change_email', token=token),
            follow_redirects=True
        )

        assert 'Your email address has been updated.' in rv.data


def test_user_cannot_change_email_with_invalid_reset_token(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        token = 'beepboopbeep'

        rv = client.get(
            url_for('auth.change_email', token=token),
            follow_redirects=True
        )

        assert 'Your email address has been updated.' not in rv.data


def test_user_can_confirm_account_with_valid_token(mockdata, client, session):
    with current_app.test_request_context():
        login_unconfirmed_user(client)
        user = User.query.filter_by(email='freddy@example.org').one()
        token = user.generate_confirmation_token()

        rv = client.get(
            url_for('auth.confirm', token=token),
            follow_redirects=True
        )

        assert 'You have confirmed your account.' in rv.data


def test_user_can_not_confirm_account_with_invalid_token(mockdata, client,
                                                         session):
    with current_app.test_request_context():
        login_unconfirmed_user(client)
        token = 'beepboopbeep'

        rv = client.get(
            url_for('auth.confirm', token=token),
            follow_redirects=True
        )

        assert 'The confirmation link is invalid or has expired.' in rv.data


def test_user_can_change_password_if_they_match(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)
        form = ChangePasswordForm(old_password='dog',
                                  password='validpasswd',
                                  password2='validpasswd')

        rv = client.post(
            url_for('auth.change_password'),
            data=form.data,
            follow_redirects=True
        )

        assert 'Your password has been updated.' in rv.data


def login_unconfirmed_user(client):
    form = LoginForm(email='freddy@example.org',
                     password='dog',
                     remember_me=True)
    rv = client.post(
        url_for('auth.login'),
        data=form.data,
        follow_redirects=False
    )
    return rv


def test_unconfirmed_user_redirected_to_confirm_account(mockdata, client,
                                                        session):
    with current_app.test_request_context():
        login_unconfirmed_user(client)

        rv = client.get(
            url_for('auth.unconfirmed'),
            follow_redirects=False
        )

        assert 'Please Confirm Your Account' in rv.data


def test_user_cannot_change_password_if_they_dont_match(mockdata, client,
                                                        session):
    with current_app.test_request_context():
        login_user(client)
        form = ChangePasswordForm(old_password='dog',
                                  password='cat',
                                  password2='butts')

        rv = client.post(
            url_for('auth.change_password'),
            data=form.data,
            follow_redirects=True
        )

        assert 'Passwords must match' in rv.data


def test_admin_can_add_police_department(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        form = DepartmentForm(name='Test Police Department',
                              short_name='TPD')

        rv = client.post(
            url_for('main.add_department'),
            data=form.data,
            follow_redirects=True
        )

        assert 'New department' in rv.data

        # Check the department was added to the database
        department = Department.query.filter_by(
            name='Test Police Department').one()
        assert department.short_name == 'TPD'


def test_ac_cannot_add_police_department(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        form = DepartmentForm(name='Test Police Department',
                              short_name='TPD')

        rv = client.post(
            url_for('main.add_department'),
            data=form.data,
            follow_redirects=True
        )

        assert rv.status_code == 403


def test_admin_cannot_add_duplicate_police_department(mockdata, client,
                                                      session):
    with current_app.test_request_context():
        login_admin(client)

        form = DepartmentForm(name='Chicago Police Department',
                              short_name='CPD')

        rv = client.post(
            url_for('main.add_department'),
            data=form.data,
            follow_redirects=True
        )

        # Try to add the same police department again
        rv = client.post(
            url_for('main.add_department'),
            data=form.data,
            follow_redirects=True
        )

        assert 'already exists' in rv.data

        # Check that only one department was added to the database
        # one() method will throw exception if more than one department found
        department = Department.query.filter_by(
            name='Chicago Police Department').one()
        assert department.short_name == 'CPD'


def test_expected_dept_appears_in_submission_dept_selection(mockdata, client,
                                                            session):
    with current_app.test_request_context():
        login_admin(client)

        rv = client.get(
            url_for('main.submit_data'),
            follow_redirects=True
        )

        assert 'Springfield Police Department' in rv.data


def test_admin_can_add_new_officer(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)
        department = random.choice(dept_choices())
        form = AddOfficerForm(first_name='Test',
                              last_name='McTesterson',
                              middle_initial='T',
                              race='WHITE',
                              gender='M',
                              star_no=666,
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        rv = client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        assert 'McTesterson' in rv.data

        # Check the officer was added to the database
        officer = Officer.query.filter_by(
            last_name='McTesterson').one()
        assert officer.first_name == 'Test'
        assert officer.race == 'WHITE'
        assert officer.gender == 'M'


def test_ac_can_add_new_officer_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)
        department = Department.query.filter_by(id=AC_DEPT).first()
        first_name = 'Testy'
        last_name = 'OTester'
        middle_initial = 'R'
        race = random.choice(RACE_CHOICES)[0]
        gender = random.choice(GENDER_CHOICES)[0]
        form = AddOfficerForm(first_name=first_name,
                              last_name=last_name,
                              middle_initial=middle_initial,
                              race=race,
                              gender=gender,
                              star_no=666,
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        rv = client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        assert rv.status_code == 200
        assert last_name in rv.data

        # Check the officer was added to the database
        officer = Officer.query.filter_by(
            last_name=last_name).one()
        assert officer.first_name == first_name
        assert officer.race == race
        assert officer.gender == gender


def test_ac_cannot_add_new_officer_not_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)
        department = Department.query.except_(Department.query.filter_by(id=AC_DEPT)).first()
        first_name = 'Sam'
        last_name = 'Augustus'
        middle_initial = 'H'
        race = random.choice(RACE_CHOICES)[0]
        gender = random.choice(GENDER_CHOICES)[0]
        form = AddOfficerForm(first_name=first_name,
                              last_name=last_name,
                              middle_initial=middle_initial,
                              race=race,
                              gender=gender,
                              star_no=666,
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        officer = Officer.query.filter_by(last_name=last_name).first()
        assert officer is None


def test_admin_can_edit_existing_officer(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)
        department = random.choice(dept_choices())
        form = AddOfficerForm(first_name='Test',
                              last_name='Testerinski',
                              middle_initial='T',
                              race='WHITE',
                              gender='M',
                              star_no=666,
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        rv = client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        officer = Officer.query.filter_by(
            last_name='Testerinski').one()

        form = EditOfficerForm(last_name='Changed')

        rv = client.post(
            url_for('main.edit_officer', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        assert 'Changed' in rv.data
        assert 'Testerinski' not in rv.data


def test_ac_cannot_edit_officer_not_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        officer = officer = Officer.query.except_(Officer.query.filter_by(department_id=AC_DEPT)).first()
        old_last_name = officer.last_name

        new_last_name = 'Shiny'
        form = EditOfficerForm(
            last_name=new_last_name,
        )

        rv = client.post(
            url_for('main.edit_officer', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        assert rv.status_code == 403

        # Ensure changes were not made to database
        officer = Officer.query.filter_by(
            id=officer.id).one()
        assert officer.last_name == old_last_name


def test_ac_can_see_officer_not_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        officer = Officer.query.except_(Officer.query.filter_by(department_id=AC_DEPT)).first()

        rv = client.get(
            url_for('main.officer_profile', officer_id=officer.id),
            follow_redirects=True
        )

        assert rv.status_code == 200
        # Testing names doesn't work bc the way we display them varies
        assert str(officer.id) in rv.data


def test_ac_can_edit_officer_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)
        department = Department.query.filter_by(id=AC_DEPT).first()
        first_name = 'Testier'
        last_name = 'OTester'
        middle_initial = 'R'
        race = random.choice(RACE_CHOICES)[0]
        gender = random.choice(GENDER_CHOICES)[0]
        form = AddOfficerForm(first_name=first_name,
                              last_name=last_name,
                              middle_initial=middle_initial,
                              race=race,
                              gender=gender,
                              star_no=666,
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        rv = client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        officer = Officer.query.filter_by(
            last_name=last_name).one()

        new_last_name = 'Shiny'
        form = EditOfficerForm(
            first_name=first_name,
            last_name=new_last_name,
            race=race,
            gender=gender,
            department=department.id
        )

        rv = client.post(
            url_for('main.edit_officer', officer_id=officer.id),
            data=form.data,
            follow_redirects=True
        )

        assert new_last_name in rv.data
        assert last_name not in rv.data

        # Check the changes were added to the database
        officer = Officer.query.filter_by(
            id=officer.id).one()
        assert officer.last_name == new_last_name


def test_admin_adds_officer_without_middle_initial(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        department = random.choice(dept_choices())
        form = AddOfficerForm(first_name='Test',
                              last_name='McTesty',
                              race='WHITE',
                              gender='M',
                              star_no=666,
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        rv = client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        assert 'McTesty' in rv.data

        # Check the officer was added to the database
        officer = Officer.query.filter_by(
            last_name='McTesty').one()
        assert officer.first_name == 'Test'
        assert officer.middle_initial == ''
        assert officer.race == 'WHITE'
        assert officer.gender == 'M'


def test_admin_adds_officer_with_letter_in_badge_no(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        department = random.choice(dept_choices())
        form = AddOfficerForm(first_name='Test',
                              last_name='Testersly',
                              middle_initial='T',
                              race='WHITE',
                              gender='M',
                              star_no='T666',
                              rank='COMMANDER',
                              department=department.id,
                              birth_year=1990)

        rv = client.post(
            url_for('main.add_officer'),
            data=form.data,
            follow_redirects=True
        )

        assert 'Testersly' in rv.data

        # Check the officer was added to the database
        officer = Officer.query.filter_by(
            last_name='Testersly').one()
        assert officer.first_name == 'Test'
        assert officer.race == 'WHITE'
        assert officer.gender == 'M'
        assert officer.assignments[0].star_no == 'T666'


def test_admin_can_add_new_unit(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        department = Department.query.filter_by(
            name='Springfield Police Department').first()
        form = AddUnitForm(descrip='Test', department=department.id)

        rv = client.post(
            url_for('main.add_unit'),
            data=form.data,
            follow_redirects=True
        )

        assert 'New unit' in rv.data

        # Check the unit was added to the database
        unit = Unit.query.filter_by(
            descrip='Test').one()
        assert unit.department_id == department.id


def test_ac_can_add_new_unit_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        department = Department.query.filter_by(
            id=AC_DEPT).first()
        form = AddUnitForm(descrip='Test', department=department.id)

        rv = client.post(
            url_for('main.add_unit'),
            data=form.data,
            follow_redirects=True
        )

        assert 'New unit' in rv.data

        # Check the unit was added to the database
        unit = Unit.query.filter_by(
            descrip='Test').one()
        assert unit.department_id == department.id


def test_ac_cannot_add_new_unit_not_in_their_dept(mockdata, client, session):
    with current_app.test_request_context():
        login_ac(client)

        department = Department.query.except_(Department.query.filter_by(id=AC_DEPT)).first()
        form = AddUnitForm(descrip='Test', department=department.id)

        client.post(
            url_for('main.add_unit'),
            data=form.data,
            follow_redirects=True
        )

        # Check the unit was not added to the database
        unit = Unit.query.filter_by(
            descrip='Test').first()
        assert unit is None


def test_user_can_change_dept_pref(mockdata, client, session):
    with current_app.test_request_context():
        login_user(client)

        test_department_id = 1

        form = ChangeDefaultDepartmentForm(dept_pref=test_department_id)

        rv = client.post(
            url_for('auth.change_dept'),
            data=form.data,
            follow_redirects=True
        )

        assert 'Updated!' in rv.data

        user = User.query.filter_by(email='jen@example.org').one()
        assert user.dept_pref == test_department_id


def test_admin_can_update_users_to_ac(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        user = User.query.except_(User.query.filter_by(is_administrator=True)).first()
        user_id = user.id

        form = EditUserForm(
            is_area_coordinator=True,
            ac_department=AC_DEPT)

        rv = client.post(
            url_for('auth.user_api', user_id=user_id),
            data=form.data,
            follow_redirects=True
        )

        assert 'updated!' in rv.data
        assert user.is_area_coordinator is True


def test_admin_cannot_update_to_ac_without_department(mockdata, client, session):
    with current_app.test_request_context():
        login_admin(client)

        user = User.query.except_(User.query.filter_by(is_administrator=True)).first()
        user_id = user.id

        form = EditUserForm(is_area_coordinator=True)

        rv = client.post(
            url_for('auth.user_api', user_id=user_id),
            data=form.data,
            follow_redirects=True
        )

        assert 'updated!' not in rv.data
        assert user.is_area_coordinator is False


# def test_admin_can_update_users_to_admin(mockdata, client, session):
#     with current_app.test_request_context():
#         login_admin(client)

#         deparment = Department.query.get(AC_DEPT)
#         user = User.query.except_(User.query.filter_by(is_administrator=True)).first()
#         user_id = user.id

#         form = EditUserForm(
#             is_area_coordinator=False,
#             is_administrator=True)

#         rv = client.post(
#             url_for('auth.user_api', user_id=user_id),
#             data=form.data,
#             follow_redirects=True
#         )

#         assert 'updated!' in rv.data
#         assert user.is_administrator is True
