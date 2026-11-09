openapi_schema = """
openapi: 3.0.3
info:
  title: Google People API - People Get
  version: v1
  description: |-
    Provides access to information about a specific person.
  contact:
    name: Google People API Support
    url: https://developers.google.com/people
  license:
    name: Apache 2.0
    url: http://www.apache.org/licenses/LICENSE-2.0.html
servers:
  - url: https://people.googleapis.com
    description: Google People API service endpoint

components:
  securitySchemes:
    google_oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://accounts.google.com/o/oauth2/v2/auth
          tokenUrl: https://oauth2.googleapis.com/token
          scopes:
            https://www.googleapis.com/auth/contacts.readonly: See and download contacts
            https://www.googleapis.com/auth/contacts: Manage contacts (also allows read)
            https://www.googleapis.com/auth/contacts.other.readonly: See and download "Other contacts"
            https://www.googleapis.com/auth/directory.readonly: See and download contact information from the directory
            https://www.googleapis.com/auth/user.addresses.read: View your street addresses
            https://www.googleapis.com/auth/user.birthday.read: View your complete date of birth
            https://www.googleapis.com/auth/user.emails.read: View your email addresses
            https://www.googleapis.com/auth/user.gender.read: View your gender
            https://www.googleapis.com/auth/user.phonenumbers.read: View your phone numbers
            https://www.googleapis.com/auth/userinfo.email: View your email address
            https://www.googleapis.com/auth/userinfo.profile: See your personal info, including any personal info you've made publicly available
            https://www.googleapis.com/auth/profile.agerange.read: View your age range
            https://www.googleapis.com/auth/profile.language.read: View the languages you speak
  schemas:
    Person:
      type: object
      description: Information about a person.
      properties:
        resourceName:
          type: string
          description: |-
            The resource name for the person, assigned by the server.
            An ASCII string in the form of `people/{person_id}`.
          readOnly: true
        etag:
          type: string
          description: The HTTP entity tag of the resource. Used for web cache validation.
        metadata:
          $ref: '#/components/schemas/PersonMetadata'
        addresses:
          type: array
          items:
            $ref: '#/components/schemas/Address'
        ageRanges:
          type: array
          items:
            $ref: '#/components/schemas/AgeRange'
        biographies:
          type: array
          items:
            $ref: '#/components/schemas/Biography'
        birthdays:
          type: array
          items:
            $ref: '#/components/schemas/Birthday'
        calendarUrls:
          type: array
          items:
            $ref: '#/components/schemas/CalendarUrl'
        clientData:
          type: array
          items:
            $ref: '#/components/schemas/ClientData'
        coverPhotos:
          type: array
          items:
            $ref: '#/components/schemas/CoverPhoto'
        emailAddresses:
          type: array
          items:
            $ref: '#/components/schemas/EmailAddress'
        events:
          type: array
          items:
            $ref: '#/components/schemas/Event'
        externalIds:
          type: array
          items:
            $ref: '#/components/schemas/ExternalId'
        genders:
          type: array
          items:
            $ref: '#/components/schemas/Gender'
        imClients:
          type: array
          items:
            $ref: '#/components/schemas/ImClient'
        interests:
          type: array
          items:
            $ref: '#/components/schemas/Interest'
        locales:
          type: array
          items:
            $ref: '#/components/schemas/Locale'
        locations:
          type: array
          items:
            $ref: '#/components/schemas/Location'
        memberships:
          type: array
          items:
            $ref: '#/components/schemas/Membership'
        miscKeywords:
          type: array
          items:
            $ref: '#/components/schemas/MiscKeyword'
        names:
          type: array
          items:
            $ref: '#/components/schemas/Name'
        nicknames:
          type: array
          items:
            $ref: '#/components/schemas/Nickname'
        occupations:
          type: array
          items:
            $ref: '#/components/schemas/Occupation'
        organizations:
          type: array
          items:
            $ref: '#/components/schemas/Organization'
        phoneNumbers:
          type: array
          items:
            $ref: '#/components/schemas/PhoneNumber'
        photos:
          type: array
          items:
            $ref: '#/components/schemas/Photo'
        relations:
          type: array
          items:
            $ref: '#/components/schemas/Relation'
        sipAddresses:
          type: array
          items:
            $ref: '#/components/schemas/SipAddress'
        skills:
          type: array
          items:
            $ref: '#/components/schemas/Skill'
        urls:
          type: array
          items:
            $ref: '#/components/schemas/Url'
        userDefined:
          type: array
          items:
            $ref: '#/components/schemas/UserDefined'

    PersonMetadata:
      type: object
      description: Metadata about a person.
      properties:
        sources:
          type: array
          items:
            $ref: '#/components/schemas/Source'
          description: The sources of data for the person.
        previousResourceNames:
          type: array
          items:
            type: string
          description: Output only. Any former resource names this person has had. Populated only for `people.connections.list` requests specifying a sync token.
          readOnly: true
        linkedPeopleResourceNames:
          type: array
          items:
            type: string
          description: Output only. The resource names of people linked to this resource.
          readOnly: true
        deleted:
          type: boolean
          description: Output only. True if the person resource has been deleted. Populated only for `people.connections.list` requests specifying a sync token.
          readOnly: true
        objectType:
          type: string
          enum: [OBJECT_TYPE_UNSPECIFIED, PERSON, PAGE]
          description: Output only. The type of the person object.
          readOnly: true

    Source:
      type: object
      description: The source of a field.
      properties:
        type:
          type: string
          enum:
            - SOURCE_TYPE_UNSPECIFIED
            - ACCOUNT
            - PROFILE
            - DOMAIN_PROFILE
            - CONTACT
            - OTHER_CONTACT
          description: The source type.
        id:
          type: string
          description: The unique identifier within the source type.
        etag:
          type: string
          description: The HTTP entity tag of the source. Used for web cache validation.
        updateTime:
          type: string
          format: date-time
          description: Output only. The time the source was last updated.
          readOnly: true
        profileMetadata:
          $ref: '#/components/schemas/ProfileMetadata'

    ProfileMetadata:
      type: object
      description: The metadata about a profile.
      properties:
        objectType:
          type: string
          enum: [OBJECT_TYPE_UNSPECIFIED, PERSON, PAGE]
          description: The profile object type.
        userTypes:
          type: array
          items:
            type: string
            enum: [USER_TYPE_UNKNOWN, GOOGLE_USER, GPLUS_USER, GOOGLE_APPS_USER]
          description: The user types.

    FieldMetadata:
      type: object
      description: Metadata about a field.
      properties:
        primary:
          type: boolean
          description: True if this field is the primary field for all fields of this type.
        verified:
          type: boolean
          description: True if the field is verified; otherwise false.
        source:
          $ref: '#/components/schemas/Source'
        sourcePrimary:
          type: boolean
          description: Output only. True if the field is the primary field for all fields of this type on the source. Applicable only to `person.metadata.sources`.
          readOnly: true

    Date:
      type: object
      description: Represents a whole or partial calendar date.
      properties:
        year:
          type: integer
          format: int32
        month:
          type: integer
          format: int32
        day:
          type: integer
          format: int32

    Address:
      type: object
      properties:
        formattedValue:
          type: string
        type:
          type: string
        streetAddress:
          type: string
        city:
          type: string
        region:
          type: string
        postalCode:
          type: string
        country:
          type: string
        countryCode:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    AgeRange:
      type: object
      properties:
        ageRange:
          type: string
          enum: [AGE_RANGE_UNSPECIFIED, LESS_THAN_EIGHTEEN, EIGHTEEN_TO_TWENTY, TWENTY_ONE_OR_OLDER]
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Biography:
      type: object
      properties:
        value:
          type: string
        contentType:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Birthday:
      type: object
      properties:
        date:
          $ref: '#/components/schemas/Date'
        text:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    CalendarUrl:
      type: object
      properties:
        url:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    ClientData:
      type: object
      properties:
        key:
          type: string
        value:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    CoverPhoto:
      type: object
      properties:
        url:
          type: string
        default:
          type: boolean
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    EmailAddress:
      type: object
      properties:
        value:
          type: string
        formattedType:
          type: string
        type:
          type: string
        displayName:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Event:
      type: object
      properties:
        date:
          $ref: '#/components/schemas/Date'
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    ExternalId:
      type: object
      properties:
        value:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Gender:
      type: object
      properties:
        value:
          type: string
        formattedValue:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    ImClient:
      type: object
      properties:
        username:
          type: string
        formattedProtocol:
          type: string
        protocol:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Interest:
      type: object
      properties:
        value:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Locale:
      type: object
      properties:
        value:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Location:
      type: object
      properties:
        value:
          type: string
        type:
          type: string
        current:
          type: boolean
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Membership:
      type: object
      properties:
        contactGroupMembership:
          $ref: '#/components/schemas/ContactGroupMembership'
        domainMembership:
          $ref: '#/components/schemas/DomainMembership'
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    ContactGroupMembership:
      type: object
      properties:
        contactGroupId:
          type: string
        contactGroupResourceName:
          type: string
          readOnly: true

    DomainMembership:
      type: object
      properties:
        inViewerDomain:
          type: boolean

    MiscKeyword:
      type: object
      properties:
        value:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Name:
      type: object
      properties:
        displayName:
          type: string
        displayNameLastFirst:
          type: string
        familyName:
          type: string
        givenName:
          type: string
        middleName:
          type: string
        honorificPrefix:
          type: string
        honorificSuffix:
          type: string
        phoneticFamilyName:
          type: string
        phoneticGivenName:
          type: string
        phoneticMiddleName:
          type: string
        phoneticHonorificPrefix:
          type: string
        phoneticHonorificSuffix:
          type: string
        phoneticFullName:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Nickname:
      type: object
      properties:
        value:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Occupation:
      type: object
      properties:
        value:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Organization:
      type: object
      properties:
        name:
          type: string
        department:
          type: string
        title:
          type: string
        type:
          type: string
        startDate:
          $ref: '#/components/schemas/Date'
        endDate:
          $ref: '#/components/schemas/Date'
        current:
          type: boolean
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    PhoneNumber:
      type: object
      properties:
        value:
          type: string
        canonicalForm:
          type: string
          readOnly: true
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Photo:
      type: object
      properties:
        url:
          type: string
        default:
          type: boolean
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Relation:
      type: object
      properties:
        person:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    SipAddress:
      type: object
      properties:
        value:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Skill:
      type: object
      properties:
        value:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    Url:
      type: object
      properties:
        value:
          type: string
        formattedType:
          type: string
        type:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

    UserDefined:
      type: object
      properties:
        key:
          type: string
        value:
          type: string
        metadata:
          $ref: '#/components/schemas/FieldMetadata'

  parameters:
    resourceName:
      name: resourceName
      in: path
      required: true
      description: |-
        The resource name of the person.
        - To get information about the authenticated user, specify `people/me`.
        - To get information about a Google account, specify `people/{account_id}`.
        - To get information about a contact, specify the resource name that identifies the contact (e.g. `people/c123456789`).
      schema:
        type: string
        pattern: "^people/[^/]+$"
    personFields:
      name: personFields
      in: query
      description: |-
        Required. A field mask to restrict which fields on the person are returned. Multiple fields can be specified by separating them with commas.
        Valid values include: addresses, ageRanges, biographies, birthdays, calendarUrls, clientData, coverPhotos, emailAddresses, events, externalIds, genders, imClients, interests, locales, locations, memberships, metadata, miscKeywords, names, nicknames, occupations, organizations, phoneNumbers, photos, relations, sipAddresses, skills, urls, userDefined.
      required: true
      schema:
        type: string
        format: google-fieldmask
    sources:
      name: sources
      in: query
      description: |-
        Optional. A mask of what source types to return.
        Defaults to READ_SOURCE_TYPE_CONTACT and READ_SOURCE_TYPE_PROFILE if not set.
      schema:
        type: array
        items:
          type: string
          enum: [READ_SOURCE_TYPE_UNSPECIFIED, READ_SOURCE_TYPE_PROFILE, READ_SOURCE_TYPE_CONTACT, READ_SOURCE_TYPE_DOMAIN_CONTACT]
    requestMask.includeField: # Deprecated, prefer personFields
      name: requestMask.includeField
      in: query
      description: |-
        DEPRECATED (Please use personFields instead). A field mask to restrict which fields on the person are returned.
      deprecated: true
      schema:
        type: string
        format: google-fieldmask

security:
  - google_oauth2:
      - https://www.googleapis.com/auth/contacts.readonly # Default read scope

paths:
  /v1/people/me?personFields=names,emailAddresses: # Matches people/{personId} or people/me
    get:
      summary: Get a person
      description: Provides information about a person.
      operationId: people.get
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Person'
        '400':
          description: Bad Request (e.g., personFields not specified)
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
        '404':
          description: Not Found
      security:
        - google_oauth2:
            - https://www.googleapis.com/auth/contacts.readonly # Broadest read-only access
            - https://www.googleapis.com/auth/contacts # Read access if modifying scopes are also present
            - https://www.googleapis.com/auth/contacts.other.readonly
            - https://www.googleapis.com/auth/directory.readonly
            - https://www.googleapis.com/auth/user.addresses.read
            - https://www.googleapis.com/auth/user.birthday.read
            - https://www.googleapis.com/auth/user.emails.read
            - https://www.googleapis.com/auth/user.gender.read
            - https://www.googleapis.com/auth/user.phonenumbers.read
            - https://www.googleapis.com/auth/userinfo.email # Basic profile info
            - https://www.googleapis.com/auth/userinfo.profile # Basic profile info
            - https://www.googleapis.com/auth/profile.agerange.read
            - https://www.googleapis.com/auth/profile.language.read
"""
calendar_openapi_schema = """
openapi: 3.0.3
info:
  title: Google Calendar API - Events (subset)
  version: v3
  description: Minimal subset of Google Calendar API v3 used by the training agent.
servers:
  - url: https://www.googleapis.com/calendar/v3

components:
  schemas:
    EventDateTime:
      type: object
      properties:
        dateTime:
          type: string
          description: RFC3339 timestamp with offset, e.g. 2026-11-12T10:00:00+01:00.
        date:
          type: string
          description: Date (yyyy-mm-dd) for all-day events. Use either date or dateTime.
        timeZone:
          type: string
          description: IANA time zone, e.g. Europe/Warsaw.
    Attendee:
      type: object
      properties:
        email:
          type: string
          description: Attendee email address.
        optional:
          type: boolean
    Event:
      type: object
      properties:
        summary:
          type: string
          description: Title of the event.
        description:
          type: string
          description: Description / agenda of the event.
        location:
          type: string
        start:
          $ref: '#/components/schemas/EventDateTime'
        end:
          $ref: '#/components/schemas/EventDateTime'
        attendees:
          type: array
          items:
            $ref: '#/components/schemas/Attendee'
        conferenceData:
          type: object
          description: |-
            Set to {"createRequest": {"conferenceSolutionKey": {"type": "hangoutsMeet"}}}
            to attach a Google Meet link. Omit when no video call is needed.
          properties:
            createRequest:
              type: object
              properties:
                requestId:
                  type: string
                conferenceSolutionKey:
                  type: object
                  properties:
                    type:
                      type: string
                      enum: [hangoutsMeet]

paths:
  /calendars/{calendarId}/events:
    parameters:
      - name: calendarId
        in: path
        required: true
        description: Calendar identifier. Use "primary" for the signed-in user's calendar.
        schema:
          type: string
          default: primary
    get:
      operationId: calendar.events.list
      summary: List events in a time range (agenda, "what do I have tomorrow").
      parameters:
        - name: timeMin
          in: query
          description: Lower bound (RFC3339 with offset) for event end time.
          schema:
            type: string
        - name: timeMax
          in: query
          description: Upper bound (RFC3339 with offset) for event start time.
          schema:
            type: string
        - name: q
          in: query
          description: Free text search in summary, description, location, attendees.
          schema:
            type: string
        - name: maxResults
          in: query
          schema:
            type: integer
            default: 20
        - name: singleEvents
          in: query
          description: Expand recurring events. Must be true when orderBy=startTime.
          schema:
            type: boolean
            default: true
        - name: orderBy
          in: query
          schema:
            type: string
            enum: [startTime, updated]
      responses:
        '200':
          description: List of events.
    post:
      operationId: calendar.events.insert
      summary: Create a new event (meeting) in the calendar.
      parameters:
        - name: conferenceDataVersion
          in: query
          description: Must be 1 when conferenceData is provided.
          schema:
            type: integer
            enum: [0, 1]
        - name: sendUpdates
          in: query
          description: Whether to email invitations to attendees.
          schema:
            type: string
            enum: [all, externalOnly, none]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Event'
      responses:
        '200':
          description: Created event (contains htmlLink and hangoutLink).

  /calendars/{calendarId}/events/{eventId}:
    parameters:
      - name: calendarId
        in: path
        required: true
        schema:
          type: string
          default: primary
      - name: eventId
        in: path
        required: true
        schema:
          type: string
    delete:
      operationId: calendar.events.delete
      summary: Delete an event.
      parameters:
        - name: sendUpdates
          in: query
          schema:
            type: string
            enum: [all, externalOnly, none]
      responses:
        '204':
          description: Event deleted.
"""
